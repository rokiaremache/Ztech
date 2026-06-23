from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Address


class LoginForm(forms.Form):
    email    = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    email      = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name  = forms.CharField(max_length=100)
    phone      = forms.CharField(max_length=20, required=False)
    password1  = forms.CharField(widget=forms.PasswordInput)
    password2  = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model  = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar']


class AddressForm(forms.ModelForm):
    class Meta:
        model  = Address
        fields = ['full_name', 'phone', 'street', 'city', 'wilaya', 'postal_code', 'is_default']
