from django import forms
from django.core import validators
from django.forms import ModelForm
from .models import Good, Customer

class LoginForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['email', 'password']
        widgets = {
            "password": forms.PasswordInput
        }

class RegisterForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['email', 'first_name', 'last_name', 'city', 'phone', 'tg_name', 'password']
        widgets = {
            "password": forms.PasswordInput
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user