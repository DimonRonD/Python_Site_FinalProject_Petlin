from django import forms
from django.core import validators
from django.forms import ModelForm, inlineformset_factory
from .models import Good, Customer, City, GoodCategory, Advertisement, GoodImage, ImageStatus

class LoginForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['email', 'password']
        widgets = {
            "password": forms.PasswordInput
        }

class RegisterForm(ModelForm):
    city = forms.ModelChoiceField(queryset=City.objects.all(), label="Город")
    tg_name = forms.CharField(required=False, label="Telegram Имя")
    class Meta:
        model = Customer
        fields = ['email', 'first_name', 'last_name', 'city', 'phone', 'tg_name', 'password']
        widgets = {
            "password": forms.PasswordInput()
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

GoodImageFormSet = inlineformset_factory(
            Good,
            GoodImage,
            fields=['image', 'status'],
            extra=3,  # Количество полей для изображений по умолчанию
            can_delete=True
        )

class GoodImageForm(forms.ModelForm):
    class Meta:
        model = GoodImage
        fields = ['image', 'status']

class AddGood(ModelForm):
    category = forms.ModelChoiceField(queryset=GoodCategory.objects.all(), label="Категория товара")
    class Meta:
        model = Good
        fields = ['name', 'category', 'description']

class AddAd(ModelForm):
    category = forms.ModelChoiceField(queryset=GoodCategory.objects.all(), label="Категория товара")
    class Meta:
        model = Advertisement
        fields = ['name', 'category', 'description']
        widgets = {
            "password": forms.PasswordInput()
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user