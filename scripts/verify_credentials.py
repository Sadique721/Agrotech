"""
AgroTech - Credentials Verification Script
Tests: MySQL DB, Gmail SMTP Email, Cloudinary API
Reads all credentials from .env file (no hardcoded secrets)
Run: python scripts/verify_credentials.py
"""
import os, sys

# Load credentials from .env via python-decouple
try:
    from decouple import config as _cfg
    DB_HOST     = _cfg('DB_HOST')
    DB_PORT     = int(_cfg('DB_PORT', default='23778'))
    DB_NAME     = _cfg('DB_NAME', default='defaultdb')
    DB_USER     = _cfg('DB_USERNAME')
    DB_PASSWORD = _cfg('DB_PASSWORD')
    EMAIL_USER  = _cfg('EMAIL_HOST_USER')
    EMAIL_PASS  = _cfg('EMAIL_HOST_PASSWORD')
    CDN_NAME    = _cfg('CLOUDINARY_CLOUD_NAME')
    CDN_KEY     = _cfg('CLOUDINARY_API_KEY')
    CDN_SECRET  = _cfg('CLOUDINARY_API_SECRET')
except Exception as e:
    print(f"[ERROR] Could not load .env: {e}")
    sys.exit(1)

PASS = "[PASS]"
FAIL = "[FAIL]"

print("=" * 60)
print("  AgroTech - Credentials Verification")
print("=" * 60)

# 1. MySQL Database
print(f"\n[1] MySQL Database (Aiven) - {DB_HOST}")
try:
    import MySQLdb
    conn = MySQLdb.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, db=DB_NAME,
        ssl={"ca": None}, connect_timeout=10,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user WHERE is_superuser=1")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT username, email FROM auth_user WHERE is_superuser=1 LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    print(f"  {PASS} Connected to MySQL successfully!")
    print(f"  {PASS} Superusers in DB: {count} | user: {row[0]} ({row[1]})")
except Exception as e:
    print(f"  {FAIL} DB Connection failed: {e}")

# 2. Gmail SMTP Email
print(f"\n[2] Gmail SMTP ({EMAIL_USER})")
try:
    import smtplib
    smtp = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    smtp.starttls()
    smtp.login(EMAIL_USER, EMAIL_PASS)
    smtp.quit()
    print(f"  {PASS} Gmail SMTP login successful!")
    print(f"  {PASS} Email credentials are valid and working.")
except Exception as e:
    print(f"  {FAIL} Gmail SMTP failed: {e}")

# 3. Cloudinary API
print(f"\n[3] Cloudinary ({CDN_NAME})")
try:
    import cloudinary, cloudinary.api
    cloudinary.config(cloud_name=CDN_NAME, api_key=CDN_KEY, api_secret=CDN_SECRET, secure=True)
    result = cloudinary.api.resources(type="upload", prefix="agrotech/", max_results=5)
    print(f"  {PASS} Cloudinary connected!")
    print(f"  {PASS} Images found in agrotech/: {len(result['resources'])}+")
    for r in result["resources"][:3]:
        print(f"        - {r['public_id']}")
except Exception as e:
    print(f"  {FAIL} Cloudinary failed: {e}")

print("\n" + "=" * 60)
print("  Verification Complete")
print("=" * 60)
