from django.conf import settings

def agrotech_settings(request):
    return {
        'AGROTECH_HELPLINE': getattr(settings, 'AGROTECH_HELPLINE', '+91 9318302850'),
        'CDN': getattr(settings, 'CLOUDINARY_IMAGE_URLS', {}),
    }
