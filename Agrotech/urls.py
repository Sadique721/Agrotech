from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
]

# Serve user-uploaded media regardless of DEBUG mode.
# For high-traffic production, replace with a CDN or object storage (e.g., S3).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
