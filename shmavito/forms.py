from django import forms
from django.core import validators
from django.forms import ModelForm, inlineformset_factory
from django.template.context_processors import request

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
    def __init__(self, *args, **kwargs):
        # Извлекаем customer из kwargs
        self.customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)

        # Теперь можем использовать self.customer для фильтрации queryset
        if self.customer:
            self.fields['good'].queryset = Good.objects.filter(
                customer=self.customer,
                status_id=1
            ).order_by('-date')

    # category = forms.ModelChoiceField(
    #     queryset=GoodCategory.objects.all(),
    #     label="Категория товара"
    # )
    #
    # good = forms.ModelChoiceField(
    #     queryset=Good.objects.none(),
    #     label="Ваши товары"
    # )

    class Meta:
        model = Advertisement
        fields = ['name', 'description', 'sdate', 'edate', 'price']
        widgets = {
            'sdate': forms.DateInput(attrs={'type': 'date'}),
            'edate': forms.DateInput(attrs={'type': 'date'}),
        }

class Order(ModelForm):
    """
    Динамическое ограничение (например, от текущей даты)
Если ограничение зависит от текущей даты или других условий:

python
import datetime
from django import forms

class MyForm(forms.Form):
    today = datetime.date.today()
    next_month = today + datetime.timedelta(days=30)

    sdate = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': today.isoformat(),
                'max': next_month.isoformat(),
            }
        )
    )
Это создаст календарь, где пользователь может выбирать даты только в течение следующих 30 дней
    """
    pass

class EditAd(ModelForm):
    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)

        if self.customer:
            self.fields['good'].queryset = Good.objects.filter(
                customer=self.customer,
                status_id=1
            ).order_by('-date')

    category = forms.ModelChoiceField(
        queryset=GoodCategory.objects.all(),
        label="Категория товара"
    )

    good = forms.ModelChoiceField(
        queryset=Good.objects.none(),
        label="Ваши товары"
    )

    class Meta:
        model = Advertisement
        fields = ['name', 'category', 'good', 'description', 'sdate', 'edate', 'price']
        widgets = {
            'sdate': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'edate': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
        }


class EditGood(ModelForm):
    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)

        if self.customer:
            self.fields['good'].queryset = Good.objects.filter(
                customer=self.customer,
                status_id=1
            ).order_by('-date')

    category = forms.ModelChoiceField(
        queryset=GoodCategory.objects.all(),
        label="Категория товара"
    )

    good = forms.ModelChoiceField(
        queryset=Good.objects.none(),
        label="Ваши товары"
    )

    class Meta:
        model = Good
        fields = ['name', 'category', 'good', 'description']
