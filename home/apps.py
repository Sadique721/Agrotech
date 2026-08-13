from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_superuser(sender, **kwargs):
    from django.contrib.auth.models import User
    username = 'sadique721'
    email = 'mdsadiqueamin721786@gmail.com'
    password = 'Sadique@123'
    first_name = 'Md Sadique'
    last_name = 'Amin'

    try:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, 
                email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            print(f"Default superuser '{username}' successfully created.")
    except Exception:
        pass


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        # Trigger on post_migrate
        post_migrate.connect(create_default_superuser, sender=self)

