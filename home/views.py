from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils.text import slugify
from django.conf import settings
from django.db import IntegrityError
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from .models import Contact, UserProfile, NewsletterSubscriber
from .forms import UserRegistrationForm, UserProfileForm
from .data import INDIAN_STATES, WMO_WEATHER_CODES, STATE_CITIES, STATE_CROP_INFO
import requests
import datetime
import logging

logger = logging.getLogger(__name__)
import threading


def send_email_async(subject, body, to_email, html_content=None, from_email=None):
    """Helper to send standard or HTML emails in a background thread."""
    from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@agrotech.com')
    
    def _send():
        try:
            if html_content:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=body,
                    from_email=from_email,
                    to=[to_email] if isinstance(to_email, str) else to_email
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
            else:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=from_email,
                    recipient_list=[to_email] if isinstance(to_email, str) else to_email,
                    fail_silently=False
                )
        except Exception as e:
            logger.warning("Async email sending failed: %s", e)

    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()


def ratelimited_error(request, exception):
    return HttpResponse("Too many requests — please slow down and try again shortly.", status=429)


def decode_wmo_code(code):
    return WMO_WEATHER_CODES.get(code, {"desc": "Partly Cloudy", "icon": "⛅", "bg": "partly-cloudy"})

def fetch_realtime_weather_openmeteo(lat, lon, location_name):
    """Fetch live weather, extended agronomic indicators & air quality from Open-Meteo APIs."""
    cache_key = f"weather_adv_{round(lat, 2)}_{round(lon, 2)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,surface_pressure,wind_speed_10m,uv_index,dew_point_2m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,uv_index_max,et0_fao_evapotranspiration",
            "timezone": "Asia/Kolkata"
        }
        resp = requests.get(url, params=params, timeout=8)

        # Fetch Air Quality Index from Open-Meteo Air Quality API
        aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        aqi_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "pm10,pm2_5,european_aqi",
            "timezone": "Asia/Kolkata"
        }
        aqi_resp = requests.get(aqi_url, params=aqi_params, timeout=5)
        aqi_val = "N/A"
        pm25_val = "N/A"
        if aqi_resp.status_code == 200:
            aqi_data = aqi_resp.json().get("current", {})
            aqi_val = round(aqi_data.get("european_aqi", 0))
            pm25_val = round(aqi_data.get("pm2_5", 0), 1)

        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            daily = data.get("daily", {})

            w_info = decode_wmo_code(curr.get("weather_code", 0))

            # Build 7-Day Forecast list
            forecast_list = []
            dates = daily.get("time", [])
            codes = daily.get("weather_code", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            precip_probs = daily.get("precipitation_probability_max", [])
            precip_sums = daily.get("precipitation_sum", [])
            et0_list = daily.get("et0_fao_evapotranspiration", [])

            for i in range(min(len(dates), 7)):
                d_str = dates[i]
                d_obj = datetime.datetime.strptime(d_str, "%Y-%m-%d")
                if i == 0:
                    day_label = "Today"
                elif i == 1:
                    day_label = "Tomorrow"
                elif i == 2:
                    day_label = "Day After Tomorrow"
                else:
                    day_label = d_obj.strftime("%A (%b %d)")

                day_code_info = decode_wmo_code(codes[i] if i < len(codes) else 0)
                forecast_list.append({
                    "day": day_label,
                    "date": d_obj.strftime("%b %d, %Y"),
                    "temp_max": round(max_temps[i]) if i < len(max_temps) else 30,
                    "temp_min": round(min_temps[i]) if i < len(min_temps) else 20,
                    "precipitation_prob": precip_probs[i] if i < len(precip_probs) else 0,
                    "precipitation_sum": round(precip_sums[i], 1) if i < len(precip_sums) else 0.0,
                    "et0_water_loss": round(et0_list[i], 1) if i < len(et0_list) else 4.0,
                    "condition": day_code_info["desc"],
                    "icon": day_code_info["icon"],
                })

            curr_temp = round(curr.get("temperature_2m", 28))
            humidity = curr.get("relative_humidity_2m", 60)
            wind_speed = round(curr.get("wind_speed_10m", 12))
            uv_idx = round(curr.get("uv_index", 5.0), 1)
            dew_pt = round(curr.get("dew_point_2m", 20.0), 1)
            rain_prob_today = precip_probs[0] if precip_probs else 0
            et0_today = round(et0_list[0], 1) if et0_list else 4.0

            # Dynamic Agronomic Indices & Warnings
            advisories = []
            if rain_prob_today > 40:
                advisories.append("🌧️ Rain High Risk: Hold off on field irrigation & pesticide application today.")
            else:
                advisories.append(f"💧 Favorable Irrigation Window: Daily crop water requirement (ET0) is {et0_today} mm/day.")

            if wind_speed > 20:
                advisories.append("💨 High Wind Alert (>20 km/h): Avoid chemical spraying to prevent drift loss.")
            else:
                advisories.append("🎯 Optimal Spraying Window: Wind speed is favorable for pesticide & liquid fertilizer application.")

            if curr_temp > 34:
                advisories.append("🌡️ High Heat Warning: Ensure proper soil mulch & shade for young saplings.")
            elif curr_temp < 15:
                advisories.append("❄️ Cool Temperatures: Protect frost-sensitive crops during early mornings.")

            if humidity > 75 or (curr_temp - dew_pt) < 3:
                advisories.append("🌫️ High Moisture & Dew Alert: Favorable conditions for fungal/blight leaf infections.")
            else:
                advisories.append("☀️ Good Air Drying: Great conditions for crop drying & post-harvest processing.")

            if uv_idx >= 7:
                advisories.append(f"☀️ High Solar Radiation (UV Index {uv_idx}): Protect field workers and delicate nursery seedlings.")

            result = {
                "city": location_name,
                "temperature": curr_temp,
                "feels_like": round(curr.get("apparent_temperature", curr_temp)),
                "humidity": humidity,
                "pressure": round(curr.get("surface_pressure", 1013)),
                "wind_speed": wind_speed,
                "uv_index": uv_idx,
                "dew_point": dew_pt,
                "aqi": aqi_val,
                "pm2_5": pm25_val,
                "et0_today": et0_today,
                "description": w_info["desc"],
                "icon": w_info["icon"],
                "bg": w_info["bg"],
                "forecast": forecast_list,
                "advisories": advisories,
            }
            cache.set(cache_key, result, timeout=1800)  # 30 minutes
            return result
    except Exception as e:
        logger.warning("Weather API fetch error: %s", e)
        return None
    return None

def geocode_city_india(city_query):
    """Geocode any city in India safely using Open-Meteo geocoding API with URL parameters."""
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_query,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            results = data.get("results")
            if results and len(results) > 0:
                r = results[0]
                return {
                    "name": r.get("name"),
                    "state": r.get("admin1", r.get("country", "")),
                    "lat": r.get("latitude"),
                    "lon": r.get("longitude")
                }
    except Exception as e:
        logger.warning("Geocoding error: %s", e)
    return None


# --- VIEWS ---

def home(request):
    return render(request, 'index.html')


@ratelimit(key='ip', rate='20/m', method='POST', block=True)
def weather(request):
    selected_city = "Patan, Gujarat"
    lat, lon = 23.85, 72.12
    error_message = None

    if request.method == "POST":
        # Support two-dropdown: state + city OR direct text query
        state_sel = request.POST.get("state_select", "").strip()
        city_sel  = request.POST.get("city_select", "").strip()
        query     = request.POST.get("city", "").strip()

        # Priority: dropdown city > text input city
        lookup = city_sel or query
        if state_sel and not city_sel:
            lookup = state_sel  # fallback: just state selected

        if lookup:
            matched_state = next((s for s in INDIAN_STATES if s["name"].lower() == lookup.lower() or s["city"].lower() == lookup.lower() or s["state"].lower() == lookup.lower()), None)
            if matched_state:
                selected_city = matched_state["name"]
                lat, lon = matched_state["lat"], matched_state["lon"]
            else:
                geo = geocode_city_india(lookup)
                if geo:
                    selected_city = f"{geo['name']}, {geo['state']}"
                    lat, lon = geo['lat'], geo['lon']
                else:
                    error_message = f"Location '{lookup}' could not be resolved. Showing default weather for Gujarat (Patan)."
        else:
            error_message = "Please select a state and city or type a location."

    # Fetch live 100% real-time data
    weather_data = fetch_realtime_weather_openmeteo(lat, lon, selected_city)
    if weather_data is None and not error_message:
        error_message = "Weather service is temporarily unavailable. Please try again in a moment."

    # Enrich INDIAN_STATES with crop icon & image from STATE_CROP_INFO
    enriched_states = []
    for st in INDIAN_STATES:
        crop_info = STATE_CROP_INFO.get(st["state"], {"icon": "🌱", "crop": st["crops"].split(",")[0].strip(), "img": ""})
        cities = STATE_CITIES.get(st["state"], [st["city"]])
        enriched_states.append({
            **st,
            "crop_icon": crop_info["icon"],
            "crop_name": crop_info["crop"],
            "crop_img":  crop_info["img"],
            "cities":    cities,
        })

    return render(request, 'weather.html', {
        "weather_data": weather_data,
        "error_message": error_message,
        "indian_states": enriched_states,
        "state_cities_json": {st["state"]: STATE_CITIES.get(st["state"], [st["city"]]) for st in INDIAN_STATES},
        "selected_city": selected_city
    })


def about(request):
    return render(request, 'about.html')


def legends(request):
    return render(request, 'legends.html')


def services(request):
    return render(request, 'services.html')


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def service_booking(request):
    """Handle callback booking requests from the services modal and send rich HTML email to the user."""
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        service_name = request.POST.get('service_name', request.POST.get('msg', 'Smart Agriculture Service')).strip()

        if name and email:
            # 1. Store lead in database
            Contact.objects.create(name=name, email=email, msg=f"Service Booking Request: {service_name}")

            # 2. Send rich HTML confirmation email to the user (customer)
            helpline = getattr(settings, 'AGROTECH_HELPLINE', '+91 9318302850')
            subject = f"🌱 AgroTech Callback Request Confirmed: {service_name}"
            
            # Dynamically resolve service-specific email template
            service_slug = slugify(service_name).replace('-', '_')
            template_name = f"emails/services/{service_slug}.html"
            
            try:
                html_content = render_to_string(template_name, {
                    'user_name': name,
                    'service_name': service_name,
                    'helpline_number': helpline,
                })
            except TemplateDoesNotExist:
                html_content = render_to_string('emails/service_booking_email.html', {
                    'user_name': name,
                    'service_name': service_name,
                    'helpline_number': helpline,
                })
            
            # Send confirmation email to the user (customer) in the background
            body_text = f"Namaste {name},\n\nThank you for requesting callback for {service_name}. Our AgroTech team will contact you shortly.\n\nHelpline: {helpline}"
            send_email_async(
                subject=subject,
                body=body_text,
                to_email=email,
                html_content=html_content
            )

            # 3. Send notification to admin if configured in the background
            if getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', None):
                admin_body = f"Name: {name}\nEmail: {email}\nService Requested: {service_name}"
                send_email_async(
                    subject=f"New AgroTech Service Booking Request from {name}",
                    body=admin_body,
                    to_email=settings.ADMIN_NOTIFICATION_EMAIL
                )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'message': 'Callback request received successfully!'})

            messages.success(request, f"Callback request for '{service_name}' received! Check your email for confirmation.")
            return redirect('services')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Name and Email are required.'}, status=400)
            messages.error(request, "Name and Email are required fields.")
            return redirect('services')

    return redirect('services')


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        msg = request.POST.get('msg', '').strip()

        if name and email and msg:
            Contact.objects.create(name=name, email=email, msg=msg)
            if settings.ADMIN_NOTIFICATION_EMAIL:
                admin_body = f"From: {name} <{email}>\n\n{msg}"
                send_email_async(
                    subject=f"New AgroTech contact message from {name}",
                    body=admin_body,
                    to_email=settings.ADMIN_NOTIFICATION_EMAIL
                )
            messages.success(request, "Your message was successfully submitted!")
        else:
            messages.error(request, "All fields are required!")
        return redirect('contact')

    return render(request, 'contact.html')


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def newsletter_subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email:
            from .models import NewsletterSubscriber
            NewsletterSubscriber.objects.get_or_create(email=email)
            messages.success(request, "You're subscribed to AgroTech Daily Advisories!")
        else:
            messages.error(request, "Please provide a valid email address.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))



@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def registration(request):
    from .forms import UserRegistrationForm
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            
            from django.db import IntegrityError
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                UserProfile.objects.get_or_create(user=user)
                
                # Send welcome email containing credentials in the background
                html_welcome = render_to_string('emails/welcome_email.html', {
                    'username': username,
                    'password': password,
                })
                send_email_async(
                    subject="Welcome to AgroTech! 🌿",
                    body=f"Welcome to AgroTech, {username}! Your account has been created. Username: {username}, Password: {password}",
                    to_email=email,
                    html_content=html_welcome
                )
                
                messages.success(request, "Registration successful! You can now log in.")
                return redirect('login')
            except IntegrityError:
                messages.error(request, "That username or email was just taken — please try another.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UserRegistrationForm()
        
    return render(request, 'registration.html', {'form': form})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Welcome back! You have logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update related User fields
            request.user.first_name = form.cleaned_data.get('first_name', '').strip()
            request.user.last_name = form.cleaned_data.get('last_name', '').strip()
            email = form.cleaned_data.get('email', '').strip()
            if email:
                request.user.email = email
            request.user.save()

            # Handle profile picture — upload to Cloudinary, store URL in DB
            if request.POST.get('remove_picture') == 'true':
                profile.profile_picture = None
            elif 'profile_picture' in request.FILES:
                pic_file = request.FILES['profile_picture']
                try:
                    import cloudinary.uploader
                    upload_result = cloudinary.uploader.upload(
                        pic_file,
                        public_id=f"agrotech/profiles/{request.user.username}",
                        overwrite=True,
                        resource_type="image",
                        quality="auto:good",
                        fetch_format="auto",
                        width=400,
                        height=400,
                        crop="fill",
                        gravity="face",
                    )
                    profile.profile_picture = upload_result["secure_url"]
                    logger.info("Profile picture uploaded to Cloudinary for user: %s", request.user.username)
                except Exception as e:
                    logger.error("Cloudinary profile picture upload failed for %s: %s", request.user.username, e)
                    messages.error(request, "Profile picture upload failed. Please try again.")
                    return redirect('user_profile')

            # Save profile without re-triggering the file field
            profile.phone = form.cleaned_data.get('phone', '')
            profile.state = form.cleaned_data.get('state', '')
            profile.district = form.cleaned_data.get('district', '')
            profile.farm_size = form.cleaned_data.get('farm_size', '')
            profile.primary_crops = form.cleaned_data.get('primary_crops', '')
            profile.experience_years = form.cleaned_data.get('experience_years', 0)
            profile.bio = form.cleaned_data.get('bio', '')
            profile.avatar = form.cleaned_data.get('avatar', 'farmer1')
            profile.save()

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('user_profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UserProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    return render(request, 'profile.html', {
        'user': request.user,
        'profile': profile,
        'form': form
    })


def privacy_policy(request):
    return render(request, 'privacy.html')


def terms_of_use(request):
    return render(request, 'terms.html')

