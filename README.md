<!-- ========== ANIMATED HEADER BANNER ========== -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:2d6a4f,100:52b788&height=200&section=header&text=AgroTech%20Innovations&fontSize=50&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Smart%20Agriculture%20%7C%20AI%20Diagnostics%20%7C%20Live%20Weather%20%7C%20Begusarai%2C%20Bihar&descAlignY=60&descAlign=50" width="100%">
</p>

<!-- ========== TYPING SVG INTRO ========== -->
<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=24&duration=3000&pause=500&color=52B788&center=true&vCenter=true&width=600&lines=Smart+Agriculture+Platform;AI+Crop+Disease+Diagnostics;Real-Time+All-India+Weather+Portal;Direct+Farmer-to-Market+Linkage" alt="Typing SVG">
</p>

<!-- ========== PROFILE VIEWS & FOLLOWERS BADGES ========== -->
<p align="center">
  <img src="https://komarev.com/ghpvc/?username=Sadique721-Agrotech&label=Project%20Views&color=52b788&style=flat-square" alt="Project views" />
  <img src="https://img.shields.io/github/followers/Sadique721?label=Followers&style=social" alt="GitHub followers">
  <img src="https://img.shields.io/github/stars/Sadique721/Agrotech?label=Stars&style=social" alt="GitHub stars">
</p>

<p align="center">
  <a href="https://agrotech-yzl4.onrender.com"><img src="https://img.shields.io/badge/Live%20Website-agrotech--yzl4.onrender.com-10b981?style=for-the-badge&logo=render&logoColor=white" alt="Live Website"></a>
  <a href="https://github.com/Sadique721/Agrotech"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/Sadique721/Agrotech"><img src="https://img.shields.io/badge/Django-5.1.5-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"></a>
  <a href="https://open-meteo.com/"><img src="https://img.shields.io/badge/Live%20API-Open--Meteo%20Weather-0077B6?style=for-the-badge" alt="Open-Meteo API"></a>
  <a href="https://github.com/Sadique721/Agrotech/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/Sadique721/Agrotech/actions/workflows/ci.yml"><img src="https://github.com/Sadique721/Agrotech/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
</p>

---

# 🌿 AgroTech - Next-Gen Smart Agriculture Platform

<p align="center">
  <strong>Empowering 150,000+ Indian Farmers With AI, IoT Sensors, Real-Time Live Weather Intelligence & Direct Market Linkage.</strong>
</p>

---

## 📖 Table of Contents

- [Executive Overview](#-executive-overview)
- [⭐ Key Features](#-key-features)
- [🌤️ Live All-India Weather Portal](#️-live-all-india-weather-portal)
- [👤 Advanced User Profile & Photo Upload](#-advanced-user-profile--photo-upload)
- [🏆 World Agriculture Legends & Pioneers](#-world-agriculture-legends--pioneers)
- [🛠️ 16+ Modular AgroTech Services](#️-16-modular-agrotech-services)
- [🏗️ System Architecture & Tech Stack](#️-system-architecture--tech-stack)
- [🚀 Quick Installation & Local Setup](#-quick-installation--local-setup)
- [📁 Directory Structure](#-directory-structure)
- [👤 Author & Credits](#-author--credits)

---

## 📖 Executive Overview

**AgroTech Innovations** is an enterprise-grade agricultural technology ecosystem designed to bridge the gap between traditional farming wisdom and modern AI/IoT automation. Headquartered in **Begusarai, Bihar, India**, AgroTech delivers climate-resilient solutions, real-time satellite weather tracking, automated drip irrigation advisories, and direct wholesale market linkages across **all 28 States and 8 Union Territories of India**.

---

## ⭐ Features & System Status

### 🟢 Active & Implemented Features
- **🌤️ Live Caching All-India Weather Engine**: Zero-key Open-Meteo satellite API integration with coordinates geocoding. Features 30-minute coordinate-based caching, 7-day forecast lists, rain risk indicators, and dynamic crop recommendations.
- **👤 Advanced User Profiles & Photo Upload**: Interactive profile dashboard allowing users to customize farm metrics (farm size, experience years, crops, bio) with dynamic empty/unset states and secure profile picture uploads (validated using Django Media + Pillow).
- **🏆 World Agriculture Legends Page (`/legends/`)**: Dedicated history page honoring Indian and global pioneers alongside a dedicated Founder Card.
- **🛠️ AJAX Services Hub & Booking (`/services/`)**: Category filters for modular services with non-blocking AJAX fetch callbacks that prevent page navigation.
- **📩 Real Newsletter Subscriptions**: Form wired to a persistent `NewsletterSubscriber` database model and administration interface.
- **🔒 Production Security Headers**: Active rate-limiting on authentication views (`django-ratelimit`) and strict HSTS headers.

### 🟡 Technical Product Roadmap (Future Modules)
- **💧 Smart Irrigation Automation**: IoT-driven automated drip controllers mapping live soil sensors.
- **🌱 Soil Health & AI Leaf Diagnostics**: Deep-learning image analysis for pest disease identification.
- **💰 Direct Market Linkage**: Middlemen-free commodity price lookup and digital crop-trading auction house.
- **📦 Cold-Chain Logistics**: GPS-tracked transit temperature logging for farm cooperatives.

---

## 🌤️ Live All-India Weather Portal

The weather module provides **100% live satellite weather data**:
- **Current Parameters**: Temperature (°C), Feels-like temp, Relative Humidity %, Wind Speed (km/h), Air Pressure (hPa), Weather Condition icons.
- **7-Day Forecast**: Daily Min/Max temperatures and Rain Risk Probability %.
- **State Quick Pills**: One-click quick selection for Gujarat, Punjab, UP, Bihar, Maharashtra, Rajasthan, Tamil Nadu, Karnataka, Kerala, Delhi, etc.
- **Automated Advisory**: Generates crop-specific irrigation and bio-pesticide warnings based on live weather metrics.

---

## 👤 Advanced User Profile & Photo Upload

- **One-to-One UserProfile Model**: Automatically synchronized with Django's core authentication.
- **Photo Upload System**: Multipart file upload supporting JPG, PNG, WEBP with real-time JavaScript image preview.
- **4 Tabbed Dashboard Sections**:
  1. `📋 Overview & Specs` - Personal & agricultural details.
  2. `✏️ Edit Profile & Photo` - Live edit profile info & custom photo.
  3. `🛠️ Active Services` - Real-time status tags for Smart Irrigation & Soil Advisory.
  4. `🔒 Security Logs` - Session security & account metadata.

---

## 🏆 World Agriculture Legends & Pioneers

A dedicated educational portal celebrating agricultural pioneers with authentic high-resolution photos:

| Priority | Leader / Scientist | Role & Contribution | Region |
| :--- | :--- | :--- | :--- |
| **#1 FIRST** | **Md Sadique Amin** | Founder, Chief AgriTech Architect & AI Specialist | Begusarai, Bihar, India |
| **#2 SECOND** | **Dr. M.S. Swaminathan** | Father of India's Green Revolution | India |
| **#2 SECOND** | **Dr. Verghese Kurien** | Father of White Revolution (Operation Flood / Amul) | India |
| **#2 SECOND** | **Dr. Gurdev Khush** | World Food Prize Laureate & Rice Geneticist | Punjab, India |
| **#2 SECOND** | **Dr. Subhash Palekar** | Creator of Zero Budget Natural Farming (ZBNF) | Maharashtra, India |
| **#3 THIRD** | **Dr. Norman Borlaug** | Father of Global Green Revolution & Nobel Laureate | USA / Global |
| **#3 THIRD** | **George Washington Carver** | Pioneer in Agricultural Chemistry & Soil Health | USA |
| **#3 THIRD** | **Gregor Mendel** | Father of Modern Genetics | Austria |
| **#3 THIRD** | **Justus von Liebig** | Father of Agricultural Fertilizer Industry (NPK) | Germany |

---

## 🏗️ System Architecture & Tech Stack

- **Backend Framework**: Python 3.12 + Django 5.1.5
- **Frontend Architecture**: HTML5, Vanilla CSS3 (Custom Glassmorphism, CSS Grid, Flexbox), JavaScript ES6+
- **Database**: SQLite3 (Production ready for PostgreSQL / MySQL)
- **APIs Integrated**: Open-Meteo Forecast API & Geocoding API
- **Media Engine**: Pillow 12.3.0 for profile photo handling
- **Version Control**: Git & GitHub

---

## 🚀 Quick Installation & Local Setup

### Prerequisites
- Python 3.10+ installed
- Git installed

### 1. Clone Repository
```bash
git clone https://github.com/Sadique721/Agrotech.git
cd Agrotech
```

### 2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run Development Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser!

---

## 📁 Directory Structure

```
Agrotech/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions Test CI Configuration
├── Agrotech/               # Core Project Configuration
│   ├── settings.py         # App Config, Static, Media & DB Settings
│   ├── urls.py             # Root URL Dispatcher & Media Routing
│   ├── wsgi.py             # WSGI Application Entrypoint
│   └── asgi.py             # ASGI Application Entrypoint
├── home/                   # Main Django App
│   ├── models.py           # Contact, UserProfile & Newsletter Models
│   ├── views.py            # Weather API Engine, Auth & Profile Views
│   ├── urls.py             # App Route Dispatcher
│   ├── data.py             # Indian States & WMO Weather Reference Lists
│   ├── context_processors.py # Global template variables (helpline number)
│   └── migrations/         # Database Migration Files
├── templates/              # HTML Templates
│   ├── base.html           # Master Layout Header & Animated Footer
│   ├── index.html          # Enterprise Homepage & Process Flow
│   ├── profile.html        # Interactive User Profile Dashboard
│   ├── weather.html        # Live All-India Real-Time Weather Portal
│   ├── legends.html        # World Agriculture Pioneers & Leaders
│   ├── services.html       # Modular Services & AJAX Booking Modals
│   ├── about.html          # Founder Profile, Timeline & Story
│   ├── contact.html        # Contact Form & Bihar Office Address
│   ├── privacy.html        # Platform Privacy Policy
│   ├── terms.html          # Platform Terms of Use
│   ├── login.html          # Authentication Login Form
│   ├── registration.html   # User Registration Form
│   └── logout.html         # Logout Confirmation View
├── static/                 # Static Assets
│   ├── css/style.css       # Global Stylesheet
│   ├── js/script.js        # Global Mobile Menu, Scroll & Utility Scripts
│   ├── legends/            # Authentic Photos of World Agri Legends
│   └── *.webp              # High-Resolution Feature & Logo Images
├── media/                  # User Uploaded Profile Pictures
│   └── profile_pics/       # User Avatars
├── db.sqlite3              # Local SQLite Database
├── manage.py               # Django Management CLI
├── requirements.txt        # Python Dependencies (with psycopg & ratelimit)
├── .env.example            # Environment variables example configuration
├── LICENSE                 # MIT License details
├── .gitignore              # Git Ignore File
└── README.md               # Project Documentation
```

---

## 👤 Author & Credits

- **Lead Architect & Developer**: **Md Sadique Amin**
- **Location**: Begusarai, Bihar - 851101, India
- **Organization**: AgroTech Innovations
- **Contact & Support**: `support@agrotech.com` | Toll-Free: `+91 1800-AGRO-TECH`
- **GitHub Repository**: [https://github.com/Sadique721/Agrotech](https://github.com/Sadique721/Agrotech)

---

<p align="center">
  Made with ❤️ for Farmers across Bihar & India • © 2025-2026 AgroTech Innovations Pvt. Ltd.
</p>

<!-- ========== ANIMATED FOOTER WAVE ========== -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:2d6a4f,100:52b788&height=120&section=footer&width=100%">
</p>
