from django.contrib.auth.models import User
u, c = User.objects.get_or_create(username='admin')
u.email = 'mdsadiqueamin721721@gmail.com'
u.set_password('Amin@123')
u.is_staff = True
u.is_superuser = True
u.is_active = True
u.save()
status = 'CREATED' if c else 'UPDATED'
print('[OK] Superuser', status, '-> admin / Amin@123')
print('Total superusers in DB:', User.objects.filter(is_superuser=True).count())
