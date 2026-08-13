# AgroTech — Full Project Audit & Fix Playbook

> **Repo analyzed:** `Sadique721/Agrotech` (branch `main`) — Django 5.1 + SQLite + server-rendered HTML/CSS/JS
> **Analysis basis:** Full static review of every Python file, every template, Docker/Compose config, migrations, requirements, and README — not a summary, a line-by-line audit.
> **Purpose of this file:** This is both (a) a human-readable explanation of every real issue found, and (b) a ready-to-run instruction set for an AI coding agent (built for **Google Antigravity**) to actually apply the fixes.

---

## 0. How To Use This File In Antigravity

You have two ways to run this:

**Option A — Quick run (recommended to start):**
1. Open your `Agrotech` project in Antigravity.
2. Open a new Agent task in the Agent Manager.
3. Paste this entire file as your first message, and add: *"Work through this playbook top to bottom, starting with the 🔴 Critical section. After each item, show me a diff before moving to the next. Stop and ask if a fix requires a decision (e.g., which database to migrate to)."*

**Option B — Reusable Workflow (recommended if you'll iterate):**
1. Save this file as `.agent/workflows/fix-agrotech.md` in your project root.
2. In Antigravity's Agent panel, type `/fix-agrotech` to invoke it as a repeatable workflow.
3. Use the numbered **Master Fix Sequence** (Section 12) as the step list — it's written to be executed in order, since some fixes depend on earlier ones (e.g., the environment-variable setup in `SEC-1` must land before `DEPLOY-1`'s database change).

**Before you start, regardless of option:**
- Commit or back up your current `db.sqlite3` — several fixes touch models and settings.
- Work in a feature branch (`git checkout -b fix/full-audit`), not directly on `main`.
- Do the 🔴 **Critical** section first and deploy/test it before moving on — don't apply all 45 fixes in one giant uncommitted batch.
- After any model change (marked below), run `python manage.py makemigrations && python manage.py migrate`.

---

## 1. Executive Summary

| Severity | Count | Examples |
|---|---|---|
| 🔴 Critical | 15 | Hardcoded secret key, `DEBUG=True` in production, database data-loss on every redeploy, unrestricted file upload |
| 🟠 High | 10 | Zero test coverage, no rate limiting, no LICENSE file despite claiming one, silent lead loss (no email alerts) |
| 🟡 Medium | 8 | Fake default profile data, no Forms/validation layer, duplicated CSS/JS, weak admin setup |
| 🔵 Low | 7 | Dead social links, fake newsletter box, inconsistent phone numbers, missing favicon |
| ⚪ Content integrity | 4 | Marketing claims (AI/IoT/drones) with no matching code, fabricated stats/ISO badge, fake 3-person "team" |
| 🧹 Hygiene | 1 | Debug/scraping scripts committed to the repo |

**Total: 45 distinct, verified issues** — every one below was found by reading the actual file and line, not guessed. File paths and line references are given so both you and the agent can jump straight to the spot.

**The honest headline:** this is a solid-looking Django project for a portfolio/college submission — the routing, models, and Django fundamentals (CSRF tokens, auto-escaping, `create_user`, migrations) are mostly done correctly. But as shipped, it is **not** production-ready in the way the README claims: it will lose all its data on every container restart, it leaks debug information to the public internet, and roughly a third of the advertised features (AI diagnostics, IoT, drone spraying, market linkage) don't exist in the code at all — only the weather module is real. None of this is unusual for a learning project, but since you asked for a "real-time application" comparison, that's the honest gap.

---

## 2. Tech Stack Snapshot (as found, not as claimed)

| Layer | What's actually used |
|---|---|
| Backend | Django 5.1.5, Python (Dockerfile pins 3.12-slim) |
| Database | SQLite3 only (`db.sqlite3`), no abstraction for swapping engines |
| Frontend | Server-rendered Django templates, vanilla CSS (mostly inline per-page), vanilla JS |
| Auth | Django's built-in `django.contrib.auth` (session-based) |
| External APIs | Open-Meteo forecast + geocoding (free, keyless) — the **only** live external integration in the app |
| Media | Local disk via Django `ImageField` (`Pillow`) |
| Static files | WhiteNoise |
| Deployment | Docker + Gunicorn, `docker-compose.yml`, live demo on Render |
| Tests | **None** (`home/tests.py` is the unedited Django boilerplate) |
| CI/CD | **None** found, despite a "Build: Passing" badge in the README |
| App size | ~830 lines of Python (excl. migrations), ~5,010 lines of HTML templates |


---

## 3. 🔴 CRITICAL — Security & Secrets

### SEC-1: Hardcoded `SECRET_KEY` committed to the repo, and zero environment-variable architecture
**File:** `Agrotech/settings.py` line 23

**Problem:** The Django `SECRET_KEY` — used to sign sessions, password-reset tokens, and CSRF tokens — is a plaintext string committed straight into version control:
```python
SECRET_KEY = 'django-insecure-3s&*z5h-kqb33w26=z_wiji^^b*roertlu_^lqo0a0@u9lmfwx'
```
Anyone who has ever cloned this public repo has this key forever, even after you rotate it in the live app (old commits still contain it in git history). This is also the **only** config value in the whole project — nothing in `settings.py` reads from environment variables at all, which is the root cause of `SEC-2` and `SEC-3` below too.

**Impact:** Anyone with this key can forge session cookies and CSRF tokens, and tamper with any signed data your app trusts (e.g., password reset links if you add them later).

**Fix:**
1. Add `python-decouple` to `requirements.txt`.
2. Create a `.env` file in the project root (already covered by `.gitignore`) with a **freshly generated** key:
   ```
   SECRET_KEY=<generate a new one — see command below>
   DEBUG=False
   ALLOWED_HOSTS=agrotech-yzl4.onrender.com,127.0.0.1,localhost
   ```
   Generate a new key locally (never reuse the leaked one):
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
3. In `Agrotech/settings.py`, replace the top of the file:
   ```python
   from pathlib import Path
   from decouple import config, Csv

   BASE_DIR = Path(__file__).resolve().parent.parent

   SECRET_KEY = config('SECRET_KEY')
   DEBUG = config('DEBUG', default=False, cast=bool)
   ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())
   ```
4. Add the same `SECRET_KEY` / `DEBUG` / `ALLOWED_HOSTS` variables to `docker-compose.yml` under `environment:`, and to your Render dashboard's environment variables for the live deployment.
5. Immediately rotate the key on the **live** Render deployment too — the old one is permanently compromised since it's public on GitHub.

---

### SEC-2: `DEBUG = True` is hardcoded — and `docker-compose.yml`'s `DEBUG=False` does nothing
**File:** `Agrotech/settings.py` line 26, `docker-compose.yml` line 9

**Problem:** This is the single most important bug in the project. `settings.py` has:
```python
DEBUG = True
```
...as a literal Python boolean, not read from anywhere. Meanwhile `docker-compose.yml` sets:
```yaml
environment:
  - DEBUG=False
```
This environment variable is **completely inert** — nothing in `settings.py` ever calls `os.environ.get('DEBUG', ...)`, so this line gives a false sense that debug mode is off in the containerized deployment. It isn't. Every container built from this `Dockerfile` runs with Django's debug mode fully on.

**Impact:** With `DEBUG=True`, any unhandled exception shows the full Django debug page to the public internet — source code snippets, local variable values at every stack frame, all installed apps, and (in older Django debug pages) settings values. Combined with `ALLOWED_HOSTS = ['*']` (SEC-3), this is a genuinely live exposure risk on the deployed app, not a theoretical one.

**Fix:** Resolved automatically once `SEC-1`'s fix lands (`DEBUG = config('DEBUG', default=False, cast=bool)`). After that change, **verify** it actually works:
```bash
docker compose up --build
curl -i http://localhost:8000/this-page-does-not-exist/
```
You should get a plain "Not Found" (once `SEC-6`/error pages are added) — **not** a Django traceback page. If you still see a traceback, the env var isn't reaching the container.

---

### SEC-3: `ALLOWED_HOSTS = ['*']`
**File:** `Agrotech/settings.py` line 28

**Problem:** The wildcard disables Django's Host-header validation entirely, which exists specifically to stop Host-header-injection attacks (cache poisoning, password-reset-link poisoning if you add that feature later).

**Fix:** Covered by `SEC-1`'s `.env` change — set `ALLOWED_HOSTS` explicitly to your real domain(s):
```
ALLOWED_HOSTS=agrotech-yzl4.onrender.com,localhost,127.0.0.1
```
Never use `*` again, including "temporarily."

---

### SEC-4: Missing production security headers
**File:** `Agrotech/settings.py`

**Problem:** None of Django's opt-in production hardening settings are configured: no HTTPS redirect, no secure-cookie flags, no HSTS, no MIME-sniffing protection.

**Fix:** Add this block to the bottom of `settings.py`, gated on `DEBUG` so local development isn't forced onto HTTPS:
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    SECURE_HSTS_SECONDS = 3600          # start small, raise to 31536000 once confirmed stable
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
```
Deploy and re-check headers with `curl -I https://agrotech-yzl4.onrender.com/` before raising `SECURE_HSTS_SECONDS` — HSTS is sticky in browsers once set, so confirm HTTPS works cleanly first.

---

### SEC-5: Unrestricted file upload on the profile picture field
**Files:** `home/views.py` lines 511–512, `home/models.py` line 32, `templates/profile.html` line 194

**Problem:** The only "validation" on profile picture uploads is the HTML attribute `accept="image/*"` in the template — which is a UI hint for the file picker dialog, not a security control. It's trivially bypassed with browser dev tools, curl, or Postman. The view does:
```python
if 'profile_picture' in request.FILES:
    profile.profile_picture = request.FILES['profile_picture']
...
profile.save()
```
Django's `ImageField` *can* validate that a file is really an image, but only when `full_clean()` runs — which happens automatically inside `ModelForm`s, but **not** on a plain `.save()` call like this. So in practice, right now, **any file of any type and any size** can be uploaded and stored under `/media/profile_pics/`.

**Impact:** A user could upload an oversized file (disk-fill denial of service), a disguised executable, or an SVG/HTML file with embedded `<script>` that a misconfigured web server might serve as `text/html` later — a classic stored-content risk.

**Fix:** Add a real validator and call it explicitly in the view (since this code path doesn't go through a `ModelForm`).

In `home/models.py`, add above the `UserProfile` class:
```python
import os
from django.core.exceptions import ValidationError
from PIL import Image

def validate_profile_image(file):
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image must be smaller than {max_size_mb}MB.")
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Only JPG, PNG, and WEBP images are allowed.")
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        raise ValidationError("Uploaded file is not a valid image.")
    finally:
        file.seek(0)  # Image.verify() consumes the stream; reset before Django saves it
```
Then update the field:
```python
profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, validators=[validate_profile_image])
```
In `home/views.py`, validate **before** assigning, so a bad file never even reaches `.save()`:
```python
from django.core.exceptions import ValidationError
from .models import validate_profile_image

if 'profile_picture' in request.FILES:
    uploaded = request.FILES['profile_picture']
    try:
        validate_profile_image(uploaded)
        profile.profile_picture = uploaded
    except ValidationError as e:
        messages.error(request, e.message)
        return redirect('user_profile')
```
Run `python manage.py makemigrations home && python manage.py migrate` after the model change (adding a validator doesn't change the DB schema, but run it anyway to keep migration history clean if you combine this with `DATA-1`/`DATA-2`).

---

### SEC-6: Password strength rules are configured but never actually enforced
**Files:** `Agrotech/settings.py` lines 93–106, `home/views.py` lines 436–459

**Problem:** `settings.py` correctly configures `AUTH_PASSWORD_VALIDATORS` (minimum length, common-password check, etc.), which is the right instinct. But `registration()` in `views.py` creates the user directly:
```python
user = User.objects.create_user(username=username, email=email, password=password1)
```
`create_user()` does **not** call Django's password validators — those only run automatically through `UserCreationForm` or an explicit `validate_password()` call. Since this view uses neither, **any password of any strength — including `"1"` or `"password"` — is currently accepted.** The settings.py configuration is doing nothing.

**Fix:** Call the validator explicitly before creating the user, in `home/views.py`:
```python
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def registration(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required!")
        elif password1 != password2:
            messages.error(request, "Passwords do not match!")
        else:
            try:
                validate_password(password1)
            except ValidationError as e:
                for err in e.messages:
                    messages.error(request, err)
                return render(request, 'registration.html')

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                UserProfile.objects.get_or_create(user=user)
                messages.success(request, "Registration successful! You can now log in.")
                return redirect('login')

    return render(request, 'registration.html')
```
**Longer-term (recommended):** replace this manual parsing with a real `UserCreationForm` subclass — see `DATA-3`, which fixes this same root cause project-wide instead of one view at a time.

---

### SEC-7: No brute-force protection on login
**File:** `home/views.py` lines 462–477

**Problem:** `user_login()` calls `authenticate()` with no attempt limit, delay, or lockout. An attacker can script unlimited password guesses against any username.

**Fix:** Add `django-ratelimit` (`pip install django-ratelimit`, add to `requirements.txt`) and decorate the view:
```python
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def user_login(request):
    ...
```
Apply the same decorator to `registration` and `contact` (see `REL-1` for the full list — this is one instance of that broader fix).

---

### SEC-8: SSL certificate verification disabled in committed scripts
**File:** `scratch/download_khush.py` lines 12–13

**Problem:**
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
...
r = requests.get(u, headers=headers, verify=False, timeout=10)
```
`verify=False` disables TLS certificate validation, opening the request to man-in-the-middle interception — and the warning about it is explicitly silenced. This script isn't called by the running application, but it's committed to the repo, which means the pattern can get copy-pasted into real code later.

**Fix:** Covered by `HYG-1` — remove the entire `scratch/` folder from the repo. If you need to re-download any legend photos in the future, never disable `verify`; if a specific host has certificate issues, fix that host's cert or use a proper CA bundle instead.

---

### SEC-9: Container likely runs as root
**File:** `Dockerfile`

**Problem:** No `USER` instruction is set, so the container runs Gunicorn (and everything else) as `root` inside the image by default — an unnecessary privilege-escalation surface if the app or a dependency is ever compromised.

**Fix:** Add a non-root user near the end of the `Dockerfile`, after dependencies are installed and files are copied:
```dockerfile
RUN addgroup --system app && adduser --system --group app \
    && chown -R app:app /app
USER app
```
Place this **after** `RUN python manage.py collectstatic --noinput` (collectstatic needs write access to `STATIC_ROOT`, which should already be owned correctly if you `chown` before switching users).


---

## 4. 🔴 CRITICAL — Data Persistence & Deployment

### DEPLOY-1: Every container restart wipes the entire database
**Files:** `docker-compose.yml`, `Dockerfile`, `Agrotech/settings.py` lines 82–87

**Problem:** This is the most damaging bug in the project for anyone actually using the live app. The database is SQLite, stored at `db.sqlite3` inside the container's filesystem:
```python
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
```
`docker-compose.yml` mounts a volume **only** for `/app/media`:
```yaml
volumes:
  - ./media:/app/media
```
There is no volume for the SQLite file. Docker containers have an ephemeral writable layer — anything not in a mounted volume is destroyed when the container is removed/recreated (every redeploy, every crash-restart, every `docker compose down`). **Every registered user, every contact-form submission, and every profile update is lost on the next deploy.** This isn't a hypothetical edge case — it is guaranteed to happen on the very next redeploy of the current setup.

Separately: even if you *did* persist the SQLite file, running Gunicorn with multiple workers against SQLite risks `database is locked` errors under concurrent writes — SQLite is not built for multi-process concurrent write access. The README's claim that SQLite is *"Production ready for PostgreSQL / MySQL"* is a confusing sentence that papers over a real gap: nothing in the codebase currently supports switching to Postgres/MySQL at all.

**Impact:** Data loss in production, on a recurring basis, with no warning to the user.

**Fix — do one of these two, not both:**

**Option A (fastest, still not ideal for real traffic):** persist the SQLite file with a named volume.
```yaml
# docker-compose.yml
services:
  web:
    build: .
    volumes:
      - ./media:/app/media
      - sqlite_data:/app/data
    environment:
      - DATABASE_PATH=/app/data/db.sqlite3
volumes:
  sqlite_data:
```
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': config('DATABASE_PATH', default=BASE_DIR / 'db.sqlite3'),
    }
}
```

**Option B (recommended — matches what a real production app does):** migrate to PostgreSQL.
1. Add to `requirements.txt`: `psycopg[binary]>=3.1`, `dj-database-url>=2.1`
2. In `settings.py`:
   ```python
   import dj_database_url
   DATABASES = {
       'default': dj_database_url.config(
           default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
           conn_max_age=600,
       )
   }
   ```
3. Add a Postgres service to `docker-compose.yml`:
   ```yaml
   services:
     db:
       image: postgres:16-alpine
       restart: always
       environment:
         POSTGRES_DB: agrotech
         POSTGRES_USER: agrotech
         POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data
     web:
       build: .
       depends_on:
         - db
       environment:
         - DATABASE_URL=postgres://agrotech:${POSTGRES_PASSWORD}@db:5432/agrotech
       volumes:
         - ./media:/app/media
   volumes:
     postgres_data:
   ```
4. On Render (or wherever the live app is hosted), provision a managed Postgres instance and set `DATABASE_URL` in the environment.
5. Migrate existing data: `python manage.py dumpdata > backup.json` (against the old SQLite DB) before switching, then `python manage.py loaddata backup.json` after pointing at Postgres.

---

### DEPLOY-2: Media file serving is wired to `DEBUG`, so uploads will break the moment `DEBUG` is correctly turned off
**File:** `Agrotech/urls.py` lines 11–12

**Problem:**
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
This is standard Django scaffolding meant **only** for local development — it's explicitly documented as unsuitable for production. Once `SEC-2` is fixed and `DEBUG` is actually `False`, this line stops serving `/media/...` entirely, and every uploaded profile picture (`profile.profile_picture.url`) will 404.

**Fix:** WhiteNoise (already used for static files) does **not** serve user-uploaded media by design — it's meant for files baked into the image at build time, not runtime uploads. Pick one:

- **Simple:** serve media via Django regardless of `DEBUG`, acceptable for low-traffic apps:
  ```python
  # Agrotech/urls.py — remove the "if settings.DEBUG" guard
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```
  (Only reasonable if `DEPLOY-1`'s Option A or B also gives `/app/media` a real persistent volume — otherwise uploaded pictures still vanish on redeploy even if *served* correctly in between.)
- **Recommended for real production:** offload media to object storage using `django-storages` with S3-compatible storage (AWS S3, Cloudflare R2, or Render's own disk-backed persistent storage). This removes the persistence problem for media entirely, independent of container restarts.

---

### DEPLOY-3: `Dockerfile` installs PostgreSQL client libraries for a database the project doesn't use
**File:** `Dockerfile` lines 12–14

**Problem:**
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```
`libpq-dev` is the PostgreSQL client development headers — needed only to compile `psycopg2` from source. But `requirements.txt` has no `psycopg2`/`psycopg` at all, and `settings.py` only configures SQLite. This package is dead weight, inflating build time and image size for nothing.

**Fix:**
- If you adopt `DEPLOY-1` Option B (Postgres), **keep** `libpq-dev` — it's now correctly justified — but prefer `psycopg[binary]` in `requirements.txt`, which ships precompiled wheels and doesn't actually need `libpq-dev` at build time (you can then remove `libpq-dev` and `build-essential` and use a smaller image).
- If you stay on SQLite (`DEPLOY-1` Option A), **remove** `libpq-dev` (and likely `build-essential`, since nothing else in `requirements.txt` needs a C compiler) from the `Dockerfile` entirely.

---

### DEPLOY-4: Gunicorn runs on defaults — 1 worker, no timeout tuning, no structured logging
**File:** `Dockerfile` line 25

**Problem:**
```dockerfile
CMD ["sh", "-c", "python manage.py migrate && gunicorn Agrotech.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
```
With no `--workers` flag, Gunicorn defaults to **1 worker process** — meaning exactly one request is handled at a time; a slow external weather API call (see `REL-2`) blocks every other visitor until it returns or times out.

**Fix:**
```dockerfile
CMD ["sh", "-c", "python manage.py migrate && gunicorn Agrotech.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60 --access-logfile - --error-logfile -"]
```
`--workers 3` is a reasonable default for a small container (rule of thumb: `2 × CPU cores + 1`); `--access-logfile -`/`--error-logfile -` send logs to stdout/stderr so they show up in `docker logs` / Render's log viewer instead of disappearing.

---

### DEPLOY-5: `requirements.txt` has no version pinning
**File:** `requirements.txt`

**Problem:**
```
Django>=5.1.5
requests>=2.31.0
gunicorn>=21.2.0
whitenoise>=6.6.0
Pillow>=10.2.0
```
Every dependency uses an open-ended `>=`. A fresh `pip install -r requirements.txt` today can silently pull in a much newer major version of any of these than what was actually tested — including breaking changes in a future Django major release.

**Fix:** Pin exact versions that you've actually tested against, then manage upgrades deliberately:
```
Django==5.1.5
requests==2.31.0
gunicorn==21.2.0
whitenoise==6.6.0
Pillow==10.2.0
python-decouple==3.8
django-ratelimit==4.1.0
```
(version numbers above are the ones already implied by the current `>=` floors, plus the two new packages this playbook adds — bump them to whatever you actually test with). For ongoing maintenance, consider `pip-tools` (`pip-compile`) to generate a locked `requirements.txt` from a lighter `requirements.in`.

---

### DEPLOY-6: README claims a passing CI build, but no CI/CD exists
**File:** `README.md` line 24, repo root

**Problem:** The badge `Build: Passing` is a static, hardcoded shields.io badge — it's not connected to any actual pipeline. There is no `.github/workflows/` directory, no `.gitlab-ci.yml`, nothing that runs tests or builds on push.

**Fix:** Either add real CI or remove the badge — a badge that can never turn red is misleading. A minimal starting GitHub Actions workflow (`.github/workflows/ci.yml`), which also gives you a place to run the test suite once `QA-1` is fixed:
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python manage.py test
        env:
          SECRET_KEY: ci-test-key-not-for-production
          DEBUG: "False"
          ALLOWED_HOSTS: "localhost"
```


---

## 5. 🟠 HIGH — Reliability, Abuse Protection & Operability

### REL-1: No rate limiting anywhere — login, registration, contact form, and the weather lookup are all wide open
**File:** `home/views.py` (all POST-handling views)

**Problem:** Beyond the brute-force risk on login already covered in `SEC-7`, the same gap applies to:
- `registration` — a script could mass-create accounts.
- `contact` — a script could flood the `Contact` table (and, once `REL-4` is added, flood an inbox) with spam.
- `weather` — every submission triggers a live call to the external Open-Meteo API (`REL-2`); with no throttle, one script can hammer a third-party service through your server.

**Fix:** Apply `django-ratelimit` (added in `SEC-7`) consistently:
```python
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def registration(request):
    ...

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def contact(request):
    ...

@ratelimit(key='ip', rate='20/m', method='POST', block=True)
def weather(request):
    ...
```
Add a friendly response for the blocked case in `Agrotech/urls.py` / a small exception handler, since by default a rate-limited request raises `Ratelimited` (a 403). Example:
```python
# home/views.py, near the top
from ratelimit.exceptions import Ratelimited
from django.http import HttpResponse

def ratelimited_error(request, exception):
    return HttpResponse("Too many requests — please slow down and try again shortly.", status=429)
```
Wire it in `Agrotech/settings.py`: `RATELIMIT_VIEW = 'home.views.ratelimited_error'`.

---

### REL-2: No caching — every weather page load hits the external API live, with no fallback message on failure
**File:** `home/views.py` lines 259–271, 347–365

**Problem:** `fetch_realtime_weather_openmeteo()` and `geocode_city_india()` call `requests.get(...)` synchronously on **every single request**, with no caching layer, even though weather data doesn't meaningfully change second-to-second. Two consequences:
1. **Performance:** each `/weather/` view blocks a full Gunicorn worker for up to 8 seconds (the `timeout=8`) waiting on a third-party API.
2. **External rate-limit risk:** Open-Meteo's free tier has its own usage limits; a busy day (or `REL-1`'s abuse case before it's fixed) could get your server's IP throttled by Open-Meteo, breaking weather for every real visitor at once.

Additionally, when the initial page load (a plain GET, before any search) fails to fetch weather for the Gujarat/Patan default, `weather_data` becomes `None` and `error_message` stays `None` too (it's only ever set inside the `POST` branch) — the user sees a page with **no weather card and no explanation**, a silent, confusing blank state.

**Fix:** Cache successful responses with Django's cache framework (works out of the box with the zero-config default `LocMemCache` — upgrade to `django-redis` later if you run multiple Gunicorn workers, since `LocMemCache` doesn't share state across worker processes):
```python
from django.core.cache import cache

def fetch_realtime_weather_openmeteo(lat, lon, location_name):
    cache_key = f"weather_{round(lat, 2)}_{round(lon, 2)}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        # ...existing request/parsing logic unchanged...
        result = { ... }  # the existing return dict
        cache.set(cache_key, result, timeout=1800)  # 30 minutes
        return result
    except Exception as e:
        logger.warning("Weather API fetch error: %s", e)
        return None
```
And give the template a real fallback message regardless of which branch set `weather_data` to `None`, in `home/views.py`:
```python
weather_data = fetch_realtime_weather_openmeteo(lat, lon, selected_city)
if weather_data is None and not error_message:
    error_message = "Weather service is temporarily unavailable. Please try again in a moment."
```

---

### REL-3: `print()` used for error logging instead of Python's `logging` module
**File:** `home/views.py` lines 343, 364

**Problem:**
```python
except Exception as e:
    print("Weather API fetch error:", e)
    return None
```
`print()` output doesn't respect log levels, doesn't get timestamps/module context automatically, and in most production setups (Gunicorn behind a process manager) is either lost or dumped unstructured into stdout with no way to filter severity or route it to an error-tracking service later.

**Fix:** Add a standard `LOGGING` config to `Agrotech/settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'home': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
```
Then in `home/views.py`:
```python
import logging
logger = logging.getLogger(__name__)
# ...
except Exception as e:
    logger.warning("Weather API fetch error: %s", e)
    return None
```
(and the same swap for the `geocode_city_india` function's `except` block).

---

### REL-4: Contact-form and service-request leads are saved silently — nobody gets notified
**File:** `home/views.py` lines 420–433

**Problem:**
```python
if name and email and msg:
    contact_obj = Contact(name=name, email=email, msg=msg)
    contact_obj.save()
    messages.success(request, "Your message was successfully submitted!")
```
This only writes a row to the database. The same endpoint is also reused by the "Request Service Callback" modal on `services.html`, which promises the user *"Our team will contact you shortly!"* — but no email, SMS, or Slack/webhook notification exists anywhere in the codebase. Unless someone manually opens `/admin/` and checks the Contact Messages list, real leads go unnoticed indefinitely.

**Fix:** Configure email sending and notify on save. In `Agrotech/settings.py`:
```python
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
ADMIN_NOTIFICATION_EMAIL = config('ADMIN_NOTIFICATION_EMAIL', default='')
```
(`console.EmailBackend` prints emails to the terminal in dev — safe default until real SMTP credentials are supplied via `.env`.) In `home/views.py`:
```python
from django.core.mail import send_mail
from django.conf import settings

if name and email and msg:
    Contact.objects.create(name=name, email=email, msg=msg)
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
```

---

### REL-5: `contact()` doesn't follow the Post/Redirect/Get pattern
**File:** `home/views.py` lines 420–433

**Problem:** Unlike `registration`, `user_login`, and `user_profile` (all of which correctly `redirect(...)` after a successful POST), `contact()` re-renders the template directly:
```python
return render(request, 'contact.html')
```
If a user refreshes the page after submitting, the browser will prompt to resubmit the form data — and if they confirm, the same message gets saved twice.

**Fix:**
```python
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        msg = request.POST.get('msg')
        if name and email and msg:
            Contact.objects.create(name=name, email=email, msg=msg)
            messages.success(request, "Your message was successfully submitted!")
        else:
            messages.error(request, "All fields are required!")
        return redirect('contact')
    return render(request, 'contact.html')
```

---

### REL-6: No custom 404 / 500 error pages
**Files:** `templates/` (missing `404.html`, `500.html`)

**Problem:** Once `DEBUG` is correctly set to `False` (`SEC-2`), Django falls back to its own bare-bones, unbranded error pages for 404s and 500s — a jarring experience on an otherwise fully-styled site.

**Fix:** Add `templates/404.html` and `templates/500.html`. `404.html` can safely extend `base.html`:
```html
{% extends 'base.html' %}
{% block title %}Page Not Found | AgroTech{% endblock %}
{% block content %}
<div style="text-align:center; padding:80px 20px;">
    <h1>404 — Page Not Found</h1>
    <p>The page you're looking for doesn't exist. <a href="{% url 'home' %}">Go back home</a>.</p>
</div>
{% endblock %}
```
`500.html` should **not** extend `base.html` or use any context processors/URL tags — a 500 can be triggered by the very systems those depend on, so keep it self-contained plain HTML:
```html
<!DOCTYPE html>
<html><head><title>Server Error | AgroTech</title></head>
<body style="text-align:center; padding:80px 20px; font-family:Arial,sans-serif;">
    <h1>Something went wrong on our end</h1>
    <p>We've been notified. Please try again shortly.</p>
    <a href="/">Go back home</a>
</body></html>
```
No view code changes needed — Django uses these automatically when `DEBUG=False`.


---

## 6. 🟠 HIGH — Testing, Licensing & Documentation

### QA-1: Zero automated tests in the entire project
**File:** `home/tests.py` — contains only the unedited Django boilerplate (`# Create your tests here.`)

**Problem:** There is no test coverage of any kind — no model tests, no view tests, no form/validation tests. Every fix in this playbook (and every future change) is currently applied on trust alone; nothing catches a regression automatically.

**Fix:** Start with a real, runnable baseline — not a placeholder. Replace `home/tests.py`:
```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Contact, UserProfile


class ContactModelTests(TestCase):
    def test_contact_str_returns_name(self):
        c = Contact.objects.create(name="Test Farmer", email="a@example.com", msg="Hello")
        self.assertEqual(str(c), "Test Farmer")


class UserProfileSignalTests(TestCase):
    def test_profile_auto_created_on_user_creation(self):
        user = User.objects.create_user(username="farmer1", password="StrongPass123!")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())


class RegistrationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('registration')

    def test_weak_password_is_rejected(self):
        response = self.client.post(self.url, {
            'username': 'newfarmer', 'email': 'new@example.com',
            'password1': '123', 'password2': '123',
        })
        self.assertFalse(User.objects.filter(username='newfarmer').exists())

    def test_mismatched_passwords_rejected(self):
        response = self.client.post(self.url, {
            'username': 'newfarmer2', 'email': 'new2@example.com',
            'password1': 'StrongPass123!', 'password2': 'Different123!',
        })
        self.assertFalse(User.objects.filter(username='newfarmer2').exists())

    def test_valid_registration_creates_user_and_redirects(self):
        response = self.client.post(self.url, {
            'username': 'newfarmer3', 'email': 'new3@example.com',
            'password1': 'StrongPass123!', 'password2': 'StrongPass123!',
        })
        self.assertTrue(User.objects.filter(username='newfarmer3').exists())
        self.assertRedirects(response, reverse('login'))


class ContactViewTests(TestCase):
    def test_valid_submission_saves_and_redirects(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Test User', 'email': 'test@example.com', 'msg': 'Hello there',
        })
        self.assertEqual(Contact.objects.count(), 1)
        self.assertRedirects(response, reverse('contact'))

    def test_missing_fields_does_not_save(self):
        self.client.post(reverse('contact'), {'name': '', 'email': '', 'msg': ''})
        self.assertEqual(Contact.objects.count(), 0)


class PublicPagesLoadTests(TestCase):
    def test_public_pages_return_200(self):
        for name in ['home', 'about', 'services', 'legends', 'login', 'registration', 'contact']:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('user_profile'))
        self.assertEqual(response.status_code, 302)  # redirected to login
```
Run with `python manage.py test`. This isn't exhaustive (it doesn't yet cover the file-upload validator from `SEC-5` or the rate limits from `REL-1` — add those as you implement them), but it's a real, executable baseline instead of an empty file, and it will already catch regressions in the exact bugs this playbook fixes (e.g., `test_weak_password_is_rejected` will fail again if `SEC-6`'s fix is ever accidentally reverted).

---

### QA-2: README links to a LICENSE file that doesn't exist
**File:** `README.md` line 23, project root

**Problem:** The badge `[License-MIT]` links to `https://github.com/Sadique721/Agrotech/blob/main/LICENSE` — but no `LICENSE` file exists anywhere in the repository. Right now, **the project has no actual license**, which legally defaults to "all rights reserved" — meaning, ironically, nobody (including people who'd want to learn from or contribute to it) has any legal right to reuse this code, despite the badge claiming otherwise.

**Fix:** Add a real `LICENSE` file at the project root matching the MIT claim:
```
MIT License

Copyright (c) 2025 Md Sadique Amin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
(If MIT isn't actually the license you want, pick a different one at [choosealicense.com](https://choosealicense.com) — just make sure the file and the badge agree.)

---

### QA-3: No `.env.example` to document required configuration
**File:** project root (missing)

**Problem:** Once `SEC-1`, `REL-4`, and `DEPLOY-1` land, the app depends on several environment variables — but nothing in the repo tells a new developer (or future-you, six months from now) what they are or what format they expect.

**Fix:** Add `.env.example` (committed to git; the real `.env` stays gitignored):
```
SECRET_KEY=change-me-generate-a-real-one
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (leave unset to use local SQLite)
DATABASE_URL=postgres://agrotech:password@localhost:5432/agrotech

# Email (leave EMAIL_BACKEND as console.EmailBackend for local dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
ADMIN_NOTIFICATION_EMAIL=
```
Update the README's install steps (`QA-4`) to mention `cp .env.example .env` as part of setup.

---

### QA-4: README factual inconsistencies
**File:** `README.md`

**Problem — three separate accuracy issues:**
1. **Python version conflict.** The badge claims `Python 3.14`; the "Prerequisites" section says `Python 3.10+`; the actual `Dockerfile` pins `python:3.12-slim`. Three different answers to "what Python version does this need?" in the same document.
2. **Confusing database claim.** *"Database: SQLite3 (Production ready for PostgreSQL / MySQL)"* reads as if the database is already production-ready, when in fact (per `DEPLOY-1`) there's currently no working path to Postgres/MySQL at all in the code.
3. **Stale directory structure.** The documented tree omits `Dockerfile`, `docker-compose.yml`, `.dockerignore`, and the `scratch/` folder — it no longer matches the real repo layout.

**Fix:**
- Pick **one** accurate Python version (whatever the Dockerfile actually pins, e.g., `3.12`) and use it consistently in the badge and Prerequisites.
- Rephrase the database line to be honest about current state, e.g.: *"Database: SQLite3 for local development. See `DEPLOY-1` in the fix playbook for the PostgreSQL migration path used in production."*
- Regenerate the directory-structure block to match reality (and remove it from tracking `scratch/` once `HYG-1` deletes that folder).


---

## 7. 🟡 MEDIUM — Data Model & Validation

### DATA-1: New user profiles ship with fabricated, realistic-looking personal data instead of blank fields
**File:** `home/models.py` lines 33–39

**Problem:**
```python
phone = models.CharField(max_length=15, blank=True, null=True, default='+91 9876543210')
state = models.CharField(max_length=100, blank=True, null=True, default='Gujarat')
district = models.CharField(max_length=100, blank=True, null=True, default='Patan')
farm_size = models.CharField(max_length=50, blank=True, null=True, default='12.5 Acres')
primary_crops = models.CharField(max_length=200, blank=True, null=True, default='Wheat, Cotton, Groundnut')
bio = models.TextField(blank=True, null=True, default='Passionate about modern sustainable farming...')
```
Every field already allows `blank=True, null=True` — meaning there's no technical reason for the fake-but-plausible defaults. In practice, this means **every new farmer who registers and never edits their profile is shown a phone number, location, and farm size that isn't theirs.** If another user (or the profile owner themselves, confused) ever acted on that phone number or location believing it was real account data, that's a real integrity problem, not just cosmetic.

**Fix:** Drop the fake defaults; let genuinely-blank fields be blank, and handle the empty state in the template instead:
```python
phone = models.CharField(max_length=15, blank=True, null=True)
state = models.CharField(max_length=100, blank=True, null=True)
district = models.CharField(max_length=100, blank=True, null=True)
farm_size = models.CharField(max_length=50, blank=True, null=True)
primary_crops = models.CharField(max_length=200, blank=True, null=True)
bio = models.TextField(blank=True, null=True)
```
In `templates/profile.html`, show a clear call-to-action instead of silence, e.g.:
```html
{{ profile.farm_size|default:"Not set — add your farm size in Edit Profile" }}
```
Run `python manage.py makemigrations home && python manage.py migrate` after this change (it alters the model's default values).

---

### DATA-2: `experience_years` has no bounds
**File:** `home/models.py` line 38

**Problem:** `experience_years = models.IntegerField(default=5)` has no lower or upper bound at the database/model level. The view (`home/views.py` line 523) does check `.isdigit()`, but that only rejects non-numeric input — `999999999` passes fine, and anyone editing via `/admin/` bypasses the view check entirely.

**Fix:**
```python
from django.core.validators import MinValueValidator, MaxValueValidator

experience_years = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(80)])
```
Migrate afterward as above.

---

### DATA-3: No Django Forms/ModelForms used anywhere — every input is parsed by hand
**Files:** `home/views.py` (all POST-handling views)

**Problem:** `registration`, `contact`, and `user_profile` all manually pull fields with `request.POST.get(...)` and validate with `if`/`elif` chains. This is the underlying reason `SEC-6` (password validators skipped) and `SEC-5` (file validation skipped) happened in the first place — Django's Forms layer is specifically designed to apply exactly these validations automatically, re-populate the form with the user's previous input on error, and centralize error messages per field instead of one generic banner.

**Fix (recommended refactor, do after the more urgent items above):** introduce real forms. Example for registration, in a new `home/forms.py`:
```python
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, validate_profile_image

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken!")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered!")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        validate_password(password1)
        return password1

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords do not match!")
        return cleaned


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'state', 'district', 'farm_size', 'primary_crops',
                  'experience_years', 'bio', 'avatar', 'profile_picture']
```
This single change gets you username/email uniqueness checks, password validation, and file-upload validation (via the model's `validators=[validate_profile_image]` from `SEC-5`) all enforced automatically through `form.is_valid()` — and gives per-field error messages in the template via `{{ form.username.errors }}` instead of one generic banner. This is a larger refactor than the others in this playbook — do it as its own PR after the Critical/High sections are deployed and stable, since it touches views and templates together.

---

### DATA-4: Registration has a check-then-create race condition
**File:** `home/views.py` lines 447–453

**Problem:**
```python
elif User.objects.filter(username=username).exists():
    messages.error(request, "Username already taken!")
elif User.objects.filter(email=email).exists():
    messages.error(request, "Email already registered!")
else:
    user = User.objects.create_user(username=username, email=email, password=password1)
```
Between the `.exists()` check and `.create_user()`, another request for the same username could complete first. Django's `User.username` is unique at the database level, so the second request would raise an unhandled `IntegrityError` — a 500 error instead of a friendly "username taken" message. Low-probability, but a real crash path.

**Fix:** Wrap the creation in a try/except for the specific integrity error:
```python
from django.db import IntegrityError

try:
    user = User.objects.create_user(username=username, email=email, password=password1)
    UserProfile.objects.get_or_create(user=user)
    messages.success(request, "Registration successful! You can now log in.")
    return redirect('login')
except IntegrityError:
    messages.error(request, "That username or email was just taken — please try another.")
```
(This becomes unnecessary boilerplate once `DATA-3`'s form-based refactor lands, since Django's form validation + a `unique=True` constraint handles this more cleanly — but it's a cheap, immediate safety net either way.)


---

## 8. 🟡 MEDIUM — Architecture & Code Quality

### ARCH-1: A 220-line hardcoded data table lives inside the view logic file
**File:** `home/views.py` lines 13–234 (the `INDIAN_STATES` list)

**Problem:** `views.py` opens with a ~220-line Python list of dictionaries — 24 states with coordinates, crops, and pincodes — hardcoded directly in the same file as the request-handling logic. It works, but it mixes static reference data with application logic, makes the view file harder to scan, and means updating a single state's data requires a code deploy instead of a data change.

**Fix:** Move it to its own module, `home/data.py`:
```python
# home/data.py
INDIAN_STATES = [
    {"name": "Gujarat (Patan)", "city": "Patan", ...},
    # ...unchanged, just relocated...
]

WMO_WEATHER_CODES = {
    0: {"desc": "Clear Sky / Sunny", "icon": "☀️", "bg": "sunny"},
    # ...unchanged...
}
```
In `home/views.py`:
```python
from .data import INDIAN_STATES, WMO_WEATHER_CODES
```
(A database table + Django fixture is the more scalable long-term answer if this list grows or needs to be admin-editable, but relocating it out of `views.py` is the immediate win.)

---

### ARCH-2: The mobile-menu toggle function is defined twice
**Files:** `static/js/script.js` lines 6–11, `templates/base.html` lines 596–601

**Problem:** `toggleMenu()` exists in two places — once inside `static/js/script.js`'s `DOMContentLoaded` listener (assigned to `window.toggleMenu`), and again as a separate global function declaration inline in `base.html`. They currently do the same thing, so nothing visibly breaks, but it's fragile: the two copies can silently drift apart the next time either one is edited, and which one "wins" depends on script-loading order rather than being an explicit, obvious choice.

**Fix:** Keep exactly one copy. Since `script.js` is already the shared, cacheable file loaded on every page, delete the inline duplicate from `base.html`:
```html
<!-- REMOVE this whole block from base.html -->
<script>
    function toggleMenu() { ... }
    function scrollToTop() { ... }
    ...
</script>
```
Move `scrollToTop()` and the message auto-dismiss logic into `static/js/script.js` too, so all page behavior lives in one file:
```javascript
// add to static/js/script.js, inside the existing DOMContentLoaded listener
window.scrollToTop = function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function (alert) {
        alert.style.transition = 'opacity 0.5s ease';
        alert.style.opacity = '0';
        setTimeout(function () { alert.remove(); }, 500);
    });
}, 4000);
```
`base.html` then only needs `<script src="{% static 'js/script.js' %}" defer></script>` — no inline `<script>` block.

---

### ARCH-3: Nearly identical CSS is duplicated inside every single template
**Files:** all 11 files in `templates/`

**Problem:** `static/css/style.css` — the one shared, cacheable stylesheet — is only 43 lines. Every template (`about.html`, `login.html`, `registration.html`, `services.html`, etc.) instead defines its own `<style>` block, each 100–600+ lines. Common UI pieces — buttons, form inputs, card shadows, the color palette — are very likely reimplemented slightly differently in each file, since `base.html`'s reset (`* { font-family: Arial, sans-serif; }`) already shows one global rule being asserted redundantly per-page. This means: changing the site's primary brand color or button style requires editing up to 11 files instead of 1, and small visual inconsistencies between pages are almost guaranteed.

**Fix (agent task — this is a mechanical, multi-file refactor well suited to an autonomous pass):**
1. Read every `<style>` block across all 11 templates.
2. Identify rules that repeat near-verbatim across 3+ templates (candidates: `.btn`/button styles, `.alert`/`.alert-success`/`.alert-error`, form `input`/`textarea` styling, `.card`-style containers, color variables).
3. Move those shared rules into `static/css/style.css`, ideally as CSS custom properties for the palette:
   ```css
   :root {
       --color-primary: #2d6a4f;
       --color-primary-light: #52b788;
       --color-accent: #4CAF50;
       --color-bg-gradient-start: #2E8B57;
       --color-bg-gradient-end: #87CEEB;
   }
   ```
4. In each template's `{% block extra_css %}`, delete the rules now covered by `style.css`, keeping only page-specific layout rules that genuinely don't repeat elsewhere.
5. After each template is trimmed, visually diff it (screenshot before/after) to confirm nothing regressed — do this one template at a time, not all 11 in one uncommitted pass.

---

### ARCH-4: Django admin is barely configured
**File:** `home/admin.py`

**Problem:** The entire file is:
```python
from django.contrib import admin
from .models import Contact
admin.site.register(Contact)
```
Two gaps: `UserProfile` isn't registered at all, so staff can't view or manage farmer profile data through `/admin/` without dropping into the database directly. And `Contact` uses the bare default `ModelAdmin`, which will just show `Contact.__str__()` (i.e., only the name) in the list view — no email or date visible without opening each message individually, which gets unwieldy fast as submissions grow.

**Fix:**
```python
from django.contrib import admin
from .models import Contact, UserProfile

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'msg')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'district', 'experience_years', 'updated_at')
    search_fields = ('user__username', 'user__email', 'state', 'district')
    list_filter = ('state', 'avatar')
```


---

## 9. 🔵 LOW — Frontend & UX Polish

### UX-1: The footer newsletter box doesn't do anything
**File:** `templates/base.html` line 516 (appears on every page, since it's in `base.html`)

**Problem:**
```html
<form class="newsletter-form" onsubmit="event.preventDefault(); alert('Thank you for subscribing to AgroTech Daily Advisories!');">
    <input type="email" placeholder="Enter your email address..." required>
    <button type="submit" class="btn-subscribe">🔔 Subscribe Free</button>
</form>
```
This explicitly calls `preventDefault()` and shows a fake success alert — the email address is never sent anywhere or stored. A real farmer entering their email to "join 150,000+ farmers receiving daily weather advisories" is told they succeeded when nothing happened.

**Fix — pick one:**
- **Minimum:** remove the feature until it's real, so you're not showing false confirmation.
- **Real version:** add a lightweight `NewsletterSubscriber` model + view:
  ```python
  # home/models.py
  class NewsletterSubscriber(models.Model):
      email = models.EmailField(unique=True)
      subscribed_at = models.DateTimeField(auto_now_add=True)
  ```
  ```python
  # home/views.py
  def newsletter_subscribe(request):
      if request.method == "POST":
          email = request.POST.get("email", "").strip()
          if email:
              NewsletterSubscriber.objects.get_or_create(email=email)
              messages.success(request, "You're subscribed to AgroTech Daily Advisories!")
          return redirect(request.META.get('HTTP_REFERER', 'home'))
  ```
  Wire a real URL, replace the `onsubmit` JS-only fake with a genuine `method="POST" action="{% url 'newsletter_subscribe' %}"` plus `{% csrf_token %}`.

---

### UX-2: Social media icons link nowhere
**File:** `templates/base.html` lines 531–534

**Problem:** All four social icons use `href="javascript:void(0);"` — Facebook, WhatsApp, YouTube, and LinkedIn all go nowhere.

**Fix:** Either link them to your real social profiles, or remove the icons until those profiles exist — dead social links read as unfinished/untrustworthy on a public-facing business site.

---

### UX-3: "Privacy Policy" and "Terms of Use" are placeholder links with no actual page
**File:** `templates/base.html` lines 583–584

**Problem:** Same `javascript:void(0);` pattern. This is more than cosmetic here: the app collects registered users' emails, phone numbers, farm location, and uploaded photos (per `home/models.py`'s `UserProfile`) — a real Privacy Policy explaining what's collected and why is a genuine gap for any app handling personal data, not just a nice-to-have page.

**Fix:** Add two real static template views (`templates/privacy.html`, `templates/terms.html`) with genuine content describing what data `UserProfile` and `Contact` actually collect, and link the footer to them via real `{% url %}` routes instead of `javascript:void(0);`.

---

### UX-4: No favicon, no Open Graph / social-preview meta tags
**File:** `templates/base.html` `<head>`

**Problem:** No `<link rel="icon">` anywhere in the project, and no `og:title`/`og:image`/`og:description` tags — so the browser tab shows a generic icon, and sharing a link on WhatsApp/social media shows no preview card.

**Fix:** Add to `base.html`'s `<head>`:
```html
<link rel="icon" type="image/webp" href="{% static 'logo.jpg' %}">
<meta property="og:title" content="{% block og_title %}AgroTech Solutions{% endblock %}">
<meta property="og:description" content="Empowering agriculture through innovative technology.">
<meta property="og:image" content="{% static 'logo.jpg' %}">
<meta property="og:type" content="website">
```
(swap in a proper favicon-sized `.ico`/`.png` rather than reusing `logo.jpg` directly, for correct rendering in browser tabs.)

---

### UX-5: The site shows two different phone numbers
**Files:** `templates/base.html` line 567 vs `templates/contact.html` line 46

**Problem:** The footer (every page) shows `+91 1800-AGRO-TECH`; the dedicated Contact page shows `+91 9318302850`. A real visitor has no way to know which is correct.

**Fix:** Pick the real number and use it everywhere — ideally define it once as a Django template context variable (via a context processor) or a settings constant, so it's never hand-typed in two places again:
```python
# Agrotech/settings.py
CONTACT_PHONE = config('CONTACT_PHONE', default='+91 9318302850')
```
Then reference `{{ settings.CONTACT_PHONE }}` (via a small custom context processor, or pass it explicitly per-view) instead of hardcoding the string in each template.

---

### UX-6: Service-booking modal uses a blocking browser `alert()` and then silently navigates the user off the page they were on
**File:** `templates/services.html` line 217

**Problem:**
```html
<form method="POST" action="{% url 'contact' %}" onsubmit="alert('Thank you! Your request for ' + document.getElementById('modalTitle').innerText + ' has been received. Our team will contact you shortly!');">
```
This form correctly saves real data (unlike the newsletter box), but the UX is rough: submitting from the Services page pops a native browser `alert()` dialog (which feels dated and blocks interaction until dismissed), and because the form's `action` points at `/contact/`, the browser then navigates the user away from `/services/` to the Contact page — so someone browsing services who books a callback unexpectedly lands somewhere else.

**Fix:** Submit via `fetch()` so the user stays on `/services/` with an inline confirmation instead of a native alert + page navigation:
```javascript
// static/js/script.js — add inside the DOMContentLoaded listener
const bookingForm = document.querySelector('.modal-booking-box form');
if (bookingForm) {
    bookingForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(bookingForm);
        fetch(bookingForm.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        }).then(() => {
            document.getElementById('modalDesc').innerText =
                "Thanks! Your request has been received — our team will contact you shortly.";
        });
    });
}
```
(Pairs well with `REL-4`'s email notification, so a real person actually sees these bookings.)

---

### UX-7: Leftover debug `console.log` in production JavaScript
**File:** `static/js/script.js` line 40

**Problem:** `console.log('AgroTech JS loaded successfully.');` runs on every single page load in production — harmless, but it's debug scaffolding that should have been removed before shipping.

**Fix:** Delete the line (or guard it behind a `DEBUG`-style flag if you want it for local development only).


---

## 10. ⚪ Content Integrity — "Real Application" Credibility Gaps

These aren't code bugs — the app runs fine either way — but since the ask was specifically to compare this against a *real* production application, these matter just as much for a genuine launch. Framed constructively, not as a criticism of the work itself.

### CONTENT-1: The README and homepage advertise features that don't exist in the code
**Files:** `README.md`, `templates/index.html`, `templates/base.html` (footer)

**Problem:** The README banner and homepage promise *"AI Crop Disease Diagnostics," "IoT Sensors," "Automated Drip Irrigation,"* *"Precision Drone Spraying,"* and *"Direct Market Linkage."* After reading every Python file in the project: the **only** real, working feature is the weather module (`fetch_realtime_weather_openmeteo`, backed by the genuinely-live Open-Meteo API). There is no AI model, no IoT integration, no drone control, no marketplace/transaction logic anywhere in `home/models.py` or `home/views.py`. The "16+ Modular AgroTech Services" page (`services.html`) is a set of static informational cards with one shared contact-callback form — a lead-capture UI, not 16 working services.

**Fix:** For each advertised feature, either build a minimal real version, or relabel it honestly. A middle ground that's common in real product READMEs — and won't require rewriting the whole homepage — is an explicit **"Implemented" vs. "Roadmap"** split:
```markdown
## ✅ Implemented Today
- Live all-India weather + 7-day forecast (Open-Meteo)
- User registration, login, and editable farmer profile
- Contact / service-callback form

## 🚧 Roadmap (not yet built)
- AI-based crop disease diagnostics
- IoT soil-sensor integration
- Drone-based precision spraying
- Direct farmer-to-market transaction linkage
```
This is a completely normal, credible thing for a growing project's README to say, and it's far more trustworthy than implying everything already works.

---

### CONTENT-2: Fabricated-looking trust signals — stat counters, an ISO certification claim, and a fictional 3-person team
**Files:** `templates/index.html` lines 9, 21, 29; `templates/base.html` line 579; `templates/about.html` lines 152–170

**Problem, with the three concrete instances:**
1. **Stats:** the homepage hero shows *"500,000+ acres digitized," "3.5M Liters water saved,"* and *"150,000+ Indian Farmers"* as static text — there is no `Farm`/`Acreage`/`WaterSaved` model anywhere backing these numbers; they can't be measured from anything the app actually tracks.
2. **Certification:** the footer states *"ISO 9001:2025 Certified"* — ISO 9001 certification is a real, audited, paid accreditation process; nothing in the repo suggests this organization holds one.
3. **Team:** `about.html` shows a "Founder & CEO," "CTO," and "CMO" (three separate people, three separate photos) — but the README's own "Author & Credits" section names a single developer (`Md Sadique Amin`) as the sole architect. Presenting a fabricated multi-person leadership team is the kind of thing that actively damages trust if a visitor (an investor, a real farmer doing diligence, a recruiter) ever checks.

**Fix:** For a solo/student project, the honest and still-impressive framing is to own it: *"Built solo by Md Sadique Amin"* is a genuinely strong credential and doesn't need three invented executives to back it. Replace or remove the fake stat counters (or clearly label them as illustrative/target figures, e.g., *"Our goal: reach 150,000 farmers"*), and drop the ISO claim unless it's real.

---

### CONTENT-3: The "World Agriculture Legends" page ranks the developer above the scientists it's honoring
**File:** `templates/legends.html`, `README.md` lines 95–105

**Problem:** The legends table lists **"Md Sadique Amin"** at priority `#1 FIRST`, ahead of Dr. M.S. Swaminathan (the actual, widely-credited Father of India's Green Revolution), Dr. Norman Borlaug (Nobel Peace Prize laureate), and Gregor Mendel (founder of modern genetics). This is a page explicitly framed as honoring historical pioneers — putting yourself above Nobel laureates on your own hall-of-fame page reads as self-promotional in a way that undercuts the page's credibility, even though the impulse to credit yourself as the platform's builder is completely reasonable.

**Fix:** Keep a "Founder's Note" or a separate "About the Creator" card elsewhere on the page (or link to the About page) — but let the actual ranked list be ordered by the real historical/scientific criteria the page claims to use (chronological, or by global impact), with the real legends first.

---

### CONTENT-4: Legend photos were sourced by scripts with disabled SSL verification — licensing should be verified before this stays live
**File:** `scratch/download_khush.py`, `scratch/download_legends.py`, `static/legends/`

**Problem:** The images used for the Legends page were downloaded from third-party sources (Wikipedia, worldfoodprize.org, and a CloudFront-hosted asset) via ad-hoc scripts, with no attribution stored or license check performed — separate from `SEC-8`'s security issue with those same scripts.

**Fix:** Before this page stays live on a public production domain, verify each image's actual license/usage rights (Wikipedia/Wikimedia Commons images are often — but not always — Creative Commons and require attribution; World Food Prize's own site content is typically not freely licensed for reuse). Add an attribution line/credit under each photo where required, or replace with confirmed-licensed alternatives.

---

## 11. 🧹 Repository Hygiene

### HYG-1: A folder of personal one-off scripts is committed to the main repository
**File:** `scratch/` (4 files: `download_khush.py`, `download_khush_final.py`, `download_legends.py`, `find_khush.py`)

**Problem:** These are one-time image-downloading utility scripts the developer used locally while building the Legends page — not part of the running Django application (nothing in `home/` or `Agrotech/` imports them). One of them contains a hardcoded Windows path (`d:\Githube\New folder\Agrotech\static\legends\gurdev_khush.jpg`), leaking local machine/folder-structure details into a public repo, and (per `SEC-8`) disables TLS verification.

**Fix:**
```bash
git rm -r scratch/
```
Add `scratch/` to `.gitignore` if you want to keep using a local scratch folder for future one-off scripts (it's already correctly excluded in `.dockerignore`, just not in `.gitignore` or git history).


---

## 12. ✅ Master Fix Sequence (for the Antigravity agent)

Execute in this order. Each phase is independently testable — commit and verify after each one before starting the next. Skipping ahead risks fixes that depend on earlier config (e.g., email notifications need the `.env` setup from Phase 1) failing silently.

**Phase 1 — Foundation (do first, everything else depends on this)**
1. Add `python-decouple` to `requirements.txt`; implement `SEC-1` (env-based `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS`, new `.env`, generate a fresh key, never reuse the committed one).
2. Add `QA-3`'s `.env.example` to the repo.
3. Delete the `scratch/` folder per `HYG-1` (this also fully resolves `SEC-8` — no separate action needed).
4. Add the non-root `USER` directive to the `Dockerfile` per `SEC-9`.
5. **Checkpoint:** `docker compose up --build` still runs; app loads locally with the new `.env`.

**Phase 2 — Close the critical security holes**
6. `SEC-2`: confirm `DEBUG` now genuinely responds to the env var (test with `curl` against a 404 URL).
7. `SEC-3`: set real `ALLOWED_HOSTS` values.
8. `SEC-4`: add the production security-headers block to `settings.py`.
9. `SEC-5`: add `validate_profile_image`, wire it into the model and the view.
10. `SEC-6`: call `validate_password()` explicitly in `registration`.
11. `SEC-7` + `REL-1`: add `django-ratelimit` to `requirements.txt`; decorate `user_login`, `registration`, `contact`, `weather`.
12. **Checkpoint:** run `python manage.py check --deploy` — it should report far fewer warnings than before this phase.

**Phase 3 — Data persistence & deployment**
13. Decide SQLite-with-volume vs. PostgreSQL for `DEPLOY-1` (recommend Postgres — flag this decision to the user if running unattended, don't guess silently).
14. Apply `DEPLOY-1`'s chosen fix, update `docker-compose.yml` accordingly.
15. `DEPLOY-2`: fix media serving to match the persistence decision made in step 13–14.
16. `DEPLOY-3`: reconcile `libpq-dev` in the `Dockerfile` with the database decision.
17. `DEPLOY-4`: tune the Gunicorn `CMD` (workers/timeout/logging).
18. `DEPLOY-5`: pin exact versions in `requirements.txt` for every package touched so far.
19. **Checkpoint:** `docker compose down && docker compose up --build`, create a test user, restart the container, confirm the test user still exists.

**Phase 4 — Reliability & operability**
20. `REL-2`: add caching to the weather-fetching functions; add the missing fallback error message.
21. `REL-3`: add `LOGGING` config to `settings.py`; replace both `print()` calls in `views.py` with `logger.warning(...)`.
22. `REL-4`: add `EMAIL_*` settings and `send_mail()` call in `contact()`.
23. `REL-5`: fix `contact()` to redirect after POST.
24. `REL-6`: add `templates/404.html` and `templates/500.html`.
25. **Checkpoint:** submit the contact form twice in a row via browser refresh — confirm no duplicate resubmission prompt; visit a nonexistent URL — confirm the styled 404 page (only visible when `DEBUG=False`).

**Phase 5 — Data model correctness**
26. `DATA-1`: remove fake defaults from `UserProfile` fields; update `profile.html` to show a real empty state.
27. `DATA-2`: add `MinValueValidator`/`MaxValueValidator` to `experience_years`.
28. `DATA-4`: wrap registration's `create_user()` call in a try/except for `IntegrityError`.
29. Run `python manage.py makemigrations home && python manage.py migrate` once for all of Phase 5's model changes together (avoid a separate migration per field).

**Phase 6 — Code quality & architecture**
30. `ARCH-1`: move `INDIAN_STATES` and `WMO_WEATHER_CODES` into `home/data.py`.
31. `ARCH-2`: remove the duplicate inline `toggleMenu()`/`scrollToTop()` from `base.html`; consolidate into `script.js`.
32. `ARCH-4`: register `UserProfile` in `admin.py`; add `list_display`/`search_fields` to both admin classes.

**Phase 7 — Frontend & UX polish**
33. `UX-1`: make the newsletter form real (or remove it) — flag this choice to the user rather than assuming.
34. `UX-2`, `UX-3`: fix or remove dead social/privacy/terms links.
35. `UX-4`: add favicon + Open Graph tags.
36. `UX-5`: unify the two conflicting phone numbers into one source of truth.
37. `UX-6`: convert the service-booking modal to an AJAX submission.
38. `UX-7`: remove the stray `console.log`.

**Phase 8 — Testing & CI**
39. `QA-1`: replace `home/tests.py` with the real test suite from this playbook; extend it to cover each fix made in Phases 2–7 as you go.
40. `DEPLOY-6`: add the GitHub Actions CI workflow that runs `python manage.py test` on every push.

**Phase 9 — Content honesty & documentation**
41. `CONTENT-1`: split the README/homepage into "Implemented" vs. "Roadmap" — **flag this to the user for approval before publishing**, since it changes the site's public claims.
42. `CONTENT-2`, `CONTENT-3`: **flag to the user** — these involve removing/reframing content about the team, stats, and the legends ranking; don't auto-apply without confirmation.
43. `CONTENT-4`: verify legend photo licenses; add attribution or replace as needed.
44. `QA-2`: add the real `LICENSE` file.
45. `QA-4`: correct the README's Python version, database phrasing, and directory structure once everything above has landed.

**Phase 10 — Optional larger refactors (separate PRs, not urgent)**
- `DATA-3`: introduce `home/forms.py` and migrate `registration`/`user_profile` to use it.
- `ARCH-3`: consolidate the duplicated per-template CSS into `static/css/style.css`.


---

## 13. 🔍 Post-Fix Verification Checklist

Manual QA to run after each phase above — don't just trust that the code changed, confirm the behavior changed:

- [ ] `python manage.py check --deploy` shows no unresolved warnings.
- [ ] Fresh `git clone` + `docker compose up --build` works end-to-end with only `.env` (never the old hardcoded secret) supplied.
- [ ] Trigger a 500 (e.g., temporarily break a view) with `DEBUG=False` — confirm **no** stack trace, source code, or settings values are shown to the browser.
- [ ] Restart the container (`docker compose restart` or a full `down && up`) — confirm a previously-registered test user **still exists** and can log in.
- [ ] Try uploading a `.txt` file renamed to `.jpg` as a profile picture — confirm it's rejected with a clear error, not silently accepted.
- [ ] Register with password `"password"` — confirm it's rejected.
- [ ] Submit the login form 10 times rapidly with a wrong password — confirm rate limiting kicks in.
- [ ] Submit the contact form, then hit browser refresh — confirm no "confirm resubmission" prompt and no duplicate row in `Contact`.
- [ ] Check that a contact-form submission triggers a real email (or, at minimum, appears in the console backend's output in dev).
- [ ] Visit `/weather/` twice in a row for the same city within a minute — confirm the second load is faster (cache hit) via added logging or a debug print you remove afterward.
- [ ] Load every page on mobile width (~375px) — confirm the hamburger menu still works after the JS de-duplication in `ARCH-2`.
- [ ] Run `python manage.py test` — confirm all tests pass.
- [ ] Confirm the live Render deployment's environment variables are updated to match the new `.env` requirements before merging to `main` — a working local `.env` doesn't help the deployed site until Render's dashboard is updated too.

---

## 14. Appendix — Issue Map by File

| File | Issues found in this file |
|---|---|
| `Agrotech/settings.py` | SEC-1, SEC-2, SEC-3, SEC-4, SEC-6, DEPLOY-1, REL-3, REL-4 |
| `Agrotech/urls.py` | DEPLOY-2 |
| `home/views.py` | SEC-5, SEC-6, SEC-7, REL-1, REL-2, REL-3, REL-4, REL-5, DATA-3, DATA-4, ARCH-1 |
| `home/models.py` | SEC-5, DATA-1, DATA-2, ARCH-1 (`WMO_WEATHER_CODES`/`INDIAN_STATES` relocation touches `views.py`, not this file) |
| `home/admin.py` | ARCH-4 |
| `home/tests.py` | QA-1 |
| `home/urls.py` | *(no issues found — correctly structured)* |
| `Dockerfile` | SEC-9, DEPLOY-3, DEPLOY-4 |
| `docker-compose.yml` | SEC-2, DEPLOY-1 |
| `requirements.txt` | DEPLOY-5 |
| `README.md` | QA-2, QA-4, CONTENT-1, CONTENT-2, CONTENT-3 |
| *(missing)* `LICENSE` | QA-2 |
| *(missing)* `.env.example` | QA-3 |
| *(missing)* `.github/workflows/ci.yml` | DEPLOY-6 |
| *(missing)* `templates/404.html`, `templates/500.html` | REL-6 |
| `templates/base.html` | ARCH-2, UX-1, UX-2, UX-3, UX-4, UX-5 |
| `templates/services.html` | UX-6 |
| `templates/profile.html` | SEC-5, DATA-1 |
| `templates/legends.html` | CONTENT-3 |
| `templates/about.html` | CONTENT-2 |
| `templates/index.html` | CONTENT-1, CONTENT-2 |
| `templates/*.html` (all 11) | ARCH-3 (duplicated inline CSS) |
| `static/js/script.js` | ARCH-2, UX-6, UX-7 |
| `scratch/*.py` (4 files) | SEC-8, HYG-1, CONTENT-4 |

---

## Closing Notes

- Every issue above was verified by reading the actual source — none are guesses based on "what Django projects usually get wrong." Line numbers are given so you (or the agent) can jump straight to them; if you've changed the file since this was written, search for the quoted code snippet instead of trusting the line number blindly.
- The three ⚪ **Content Integrity** items and `UX-1`/`UX-2`/`UX-3` involve judgment calls about what the site *says*, not just what the code *does* — an agent should propose the change and let you approve it, not auto-publish new marketing copy on your behalf.
- Nothing here is a criticism of the project as a learning exercise — the Django fundamentals (CSRF tokens on every form, auto-escaping left on, `create_user()` for password hashing, a working migration history) are all done correctly, which is genuinely the harder part to get right. The gaps are almost entirely in the "production hardening" layer that's easy to skip until you specifically go looking for it — which is exactly what this audit did.
