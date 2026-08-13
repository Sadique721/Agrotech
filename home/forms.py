from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, validate_profile_image

class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Choose Username'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken!")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered!")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match!")
        
        if password1:
            try:
                validate_password(password1)
            except ValidationError as e:
                self.add_error('password1', e.messages)
        
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))

    class Meta:
        model = UserProfile
        fields = ['phone', 'state', 'district', 'farm_size', 'primary_crops', 'experience_years', 'bio', 'avatar', 'profile_picture']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'Mobile Number'}),
            'state': forms.TextInput(attrs={'placeholder': 'State / Region'}),
            'district': forms.TextInput(attrs={'placeholder': 'District / City'}),
            'farm_size': forms.TextInput(attrs={'placeholder': 'Total Land Area (e.g. 10 Acres)'}),
            'primary_crops': forms.TextInput(attrs={'placeholder': 'Cultivated Crops (e.g. Wheat, Rice)'}),
            'experience_years': forms.NumberInput(attrs={'placeholder': 'Years of Experience'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about your farm operations...'}),
            'avatar': forms.HiddenInput(),
        }

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            validate_profile_image(profile_picture)
        return profile_picture
