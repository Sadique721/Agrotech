from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Contact Model
class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.EmailField(max_length=122)
    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'


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

# User Profile Model for Advanced User Details & Customization
class UserProfile(models.Model):
    AVATAR_CHOICES = [
        ('farmer1', '👨‍🌾 Traditional Farmer'),
        ('farmer2', '👩‍🌾 Tech Farmer'),
        ('expert', '👨‍🔬 Agri Expert'),
        ('manager', '🚜 Farm Manager'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, validators=[validate_profile_image])
    phone = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    farm_size = models.CharField(max_length=50, blank=True, null=True)
    primary_crops = models.CharField(max_length=200, blank=True, null=True)
    
    from django.core.validators import MinValueValidator, MaxValueValidator
    experience_years = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(80)])
    bio = models.TextField(blank=True, null=True)
    avatar = models.CharField(max_length=50, choices=AVATAR_CHOICES, default='farmer1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Signal to automatically create/save UserProfile when User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Guarantee profile exists even for pre-existing users
        UserProfile.objects.get_or_create(user=instance)


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

