from django.contrib import admin
from django.urls import path
from . import views
from .views import user_logout

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("weather/", views.weather, name="weather"),
    path("legends/", views.legends, name="legends"),  # NEW PAGE: Agri Legends & Visionaries
    path("contact/", views.contact, name="contact"),
    path("registration/", views.registration, name="registration"),
    path("login/", views.user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("user_profile/", views.user_profile, name="user_profile"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("privacy/", views.privacy_policy, name="privacy_policy"),
    path("terms/", views.terms_of_use, name="terms_of_use"),
]
