from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from .models import Contact, UserProfile
import requests
import datetime
import logging

logger = logging.getLogger(__name__)


def ratelimited_error(request, exception):
    return HttpResponse("Too many requests — please slow down and try again shortly.", status=429)


from .data import INDIAN_STATES, WMO_WEATHER_CODES

def decode_wmo_code(code):
    return WMO_WEATHER_CODES.get(code, {"desc": "Partly Cloudy", "icon": "⛅", "bg": "partly-cloudy"})

def fetch_realtime_weather_openmeteo(lat, lon, location_name):
    """Fetch 100% live real-time weather & 7-day forecast from Open-Meteo API."""
    from django.core.cache import cache
    cache_key = f"weather_{round(lat, 2)}_{round(lon, 2)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,surface_pressure,wind_speed_10m&"
            f"daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max&"
            f"timezone=Asia%2FKolkata"
        )
        resp = requests.get(url, timeout=8)
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
                    "condition": day_code_info["desc"],
                    "icon": day_code_info["icon"],
                })

            # Generate dynamic agricultural advisory based on live weather
            curr_temp = round(curr.get("temperature_2m", 28))
            humidity = curr.get("relative_humidity_2m", 60)
            rain_prob_today = precip_probs[0] if precip_probs else 0

            advisories = []
            if rain_prob_today > 40:
                advisories.append("🌧️ Rain High Risk: Hold off on field irrigation & pesticide application today.")
            else:
                advisories.append("💧 Favorable Irrigation Window: Good weather for controlled watering.")

            if curr_temp > 34:
                advisories.append("🌡️ High Heat Warning: Ensure proper soil mulch & shade for young saplings.")
            elif curr_temp < 15:
                advisories.append("❄️ Cool Temperatures: Protect frost-sensitive crops during early mornings.")

            if humidity > 75:
                advisories.append("🌫️ High Moisture Alert: Watch out for fungal infections on leaf surfaces.")
            else:
                advisories.append("☀️ Good Air Drying: Great conditions for crop drying & post-harvest processing.")

            result = {
                "city": location_name,
                "temperature": curr_temp,
                "feels_like": round(curr.get("apparent_temperature", curr_temp)),
                "humidity": humidity,
                "pressure": round(curr.get("surface_pressure", 1013)),
                "wind_speed": round(curr.get("wind_speed_10m", 12)),
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
    """Geocode any city in India using Open-Meteo free geocoding API."""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_query}&count=1&language=en&format=json"
        res = requests.get(url, timeout=5)
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
        query = request.POST.get("city", "").strip()
        if query:
            # Check if query matches state preset
            matched_state = next((s for s in INDIAN_STATES if s["name"].lower() == query.lower() or s["city"].lower() == query.lower()), None)
            if matched_state:
                selected_city = matched_state["name"]
                lat, lon = matched_state["lat"], matched_state["lon"]
            else:
                geo = geocode_city_india(query)
                if geo:
                    selected_city = f"{geo['name']}, {geo['state']}"
                    lat, lon = geo['lat'], geo['lon']
                else:
                    error_message = f"Location '{query}' could not be resolved. Showing default weather for Gujarat (Patan)."
        else:
            error_message = "Please enter a state or city name."

    # Fetch live 100% real-time data
    weather_data = fetch_realtime_weather_openmeteo(lat, lon, selected_city)
    if weather_data is None and not error_message:
        error_message = "Weather service is temporarily unavailable. Please try again in a moment."

    return render(request, 'weather.html', {
        "weather_data": weather_data,
        "error_message": error_message,
        "indian_states": INDIAN_STATES,
        "selected_city": selected_city
    })


def about(request):
    return render(request, 'about.html')


def legends(request):
    return render(request, 'legends.html')


def services(request):
    return render(request, 'services.html')


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        msg = request.POST.get('msg', '').strip()

        if name and email and msg:
            Contact.objects.create(name=name, email=email, msg=msg)
            from django.core.mail import send_mail
            from django.conf import settings
            if settings.ADMIN_NOTIFICATION_EMAIL:
                try:
                    send_mail(
                        subject=f"New AgroTech contact message from {name}",
                        message=f"From: {name} <{email}>\n\n{msg}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.warning("Failed to send contact notification email: %s", e)
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

    from .forms import UserProfileForm
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

            # Handle picture removal manually if checkboxed
            if request.POST.get('remove_picture') == 'true':
                profile.profile_picture = None

            form.save()
            messages.success(request, "Your profile details and picture have been updated successfully!")
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

