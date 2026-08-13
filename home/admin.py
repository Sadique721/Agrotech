from django.contrib import admin
from .models import Contact, UserProfile, NewsletterSubscriber

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

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    list_filter = ('subscribed_at',)
    ordering = ('-subscribed_at',)

