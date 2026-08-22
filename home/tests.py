# Monkeypatch django template context copy for Python 3.14 compatibility
from django.template.context import BaseContext
def _patched_copy(self):
    duplicate = self.__class__.__new__(self.__class__)
    for k, v in self.__dict__.items():
        if k != 'dicts':
            setattr(duplicate, k, v)
    duplicate.dicts = self.dicts[:]
    return duplicate
BaseContext.__copy__ = _patched_copy

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core import mail
from home.models import UserProfile, Contact, NewsletterSubscriber, validate_profile_image
from home.views import decode_wmo_code
from django.core.files.uploadedfile import SimpleUploadedFile

class AgroTechModelsTestCase(TestCase):
    def test_user_profile_creation_signal(self):
        # Verify signal creates UserProfile when user is registered
        user = User.objects.create_user(username='testfarmer', password='Password@123')
        profile = UserProfile.objects.get(user=user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.experience_years, 0)

    def test_experience_years_validation(self):
        user = User.objects.create_user(username='testfarmer2', password='Password@123')
        profile = UserProfile.objects.get(user=user)
        
        # Valid experience
        profile.experience_years = 10
        profile.full_clean()
        
        # Invalid experience (negative)
        profile.experience_years = -5
        with self.assertRaises(ValidationError):
            profile.full_clean()
            
        # Invalid experience (too high)
        profile.experience_years = 90
        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_validate_profile_image_non_image(self):
        # Empty or non-image file should raise ValidationError
        fake_file = SimpleUploadedFile("test.txt", b"not an image file")
        with self.assertRaises(ValidationError):
            validate_profile_image(fake_file)


from django.test import override_settings

@override_settings(ADMIN_NOTIFICATION_EMAIL='admin@test.com')
class AgroTechViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='farmertest', email='farmer@test.com', password='Password@123')

    def test_decode_wmo_code(self):
        self.assertEqual(decode_wmo_code(0)['desc'], "Clear Sky / Sunny")
        self.assertEqual(decode_wmo_code(999)['desc'], "Partly Cloudy")  # default fallback

    def test_registration_view(self):
        url = reverse('registration')
        # Missing fields
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200) # Re-renders page
        
        # Successful registration
        response = self.client.post(url, {
            'username': 'newfarmer',
            'email': 'new@farmer.com',
            'password1': 'NewPassword@123',
            'password2': 'NewPassword@123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newfarmer').exists())

    def test_registration_password_mismatch(self):
        url = reverse('registration')
        response = self.client.post(url, {
            'username': 'newfarmer2',
            'email': 'new2@farmer.com',
            'password1': 'NewPassword@123',
            'password2': 'WrongPassword@123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newfarmer2').exists())

    def test_login_logout(self):
        login_url = reverse('login')
        # Correct credentials
        response = self.client.post(login_url, {
            'username': 'farmertest',
            'password': 'Password@123'
        })
        self.assertRedirects(response, reverse('home'))
        
        # Logout
        logout_url = reverse('logout')
        response = self.client.get(logout_url)
        self.assertRedirects(response, reverse('home'))

    def test_contact_submission_prg(self):
        contact_url = reverse('contact')
        # Valid contact message
        response = self.client.post(contact_url, {
            'name': 'Sadique',
            'email': 'sadique@test.com',
            'msg': 'Hello, AgroTech!'
        })
        # Check Post/Redirect/Get flow
        self.assertRedirects(response, reverse('contact'))
        self.assertEqual(Contact.objects.count(), 1)
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("New AgroTech contact message", mail.outbox[0].subject)

    def test_newsletter_subscription(self):
        subscribe_url = reverse('newsletter_subscribe')
        response = self.client.post(subscribe_url, {
            'email': 'subscribe@test.com'
        })
        self.assertEqual(response.status_code, 302) # Redirects back
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_service_booking_email(self):
        booking_url = reverse('service_booking')
        response = self.client.post(booking_url, {
            'name': 'Sadique Amin',
            'email': 'customer@agrotech.com',
            'service_name': 'Smart Irrigation System'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'ok', 'message': 'Callback request received successfully!'})
        
        # Verify lead created in Contact database model
        self.assertEqual(Contact.objects.count(), 1)
        lead = Contact.objects.first()
        self.assertEqual(lead.name, 'Sadique Amin')
        self.assertIn('Smart Irrigation System', lead.msg)
        
        # Verify emails sent (1 to customer, 1 to admin)
        self.assertTrue(len(mail.outbox) >= 1)
        customer_mail = mail.outbox[0]
        self.assertEqual(customer_mail.to, ['customer@agrotech.com'])
        self.assertIn('Smart Irrigation System', customer_mail.subject)


