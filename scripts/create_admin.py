import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Agrotech.settings')
django.setup()

from django.contrib.auth.models import User

email = 'mdsadiqueamin721721@gmail.com'
username = 'admin'
password = 'Amin@123'

user, created = User.objects.get_or_create(username=username)
user.email = email
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()

if created:
    print(f"[OK] Superuser CREATED: {username} / {password}")
else:
    print(f"[OK] Superuser UPDATED: {username} / {password}")

print(f"Email: {email}")
print(f"DB: {User.objects.filter(is_superuser=True).count()} superuser(s) in DB")
