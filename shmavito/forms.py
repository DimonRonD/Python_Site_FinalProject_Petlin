from datetime import datetime
from django.utils import timezone
from django.db.models import Avg
from django import forms
from django.core import validators
from django.forms import ModelForm, inlineformset_factory
from django.template.context_processors import request

from .models import Good, Customer, City, GoodCategory, Advertisement, GoodImage, ImageStatus, CustomerScore, Comment

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
            extra=5,  # Количество полей для изображений по умолчанию
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

    class Meta:
        model = Advertisement
        fields = ['name', 'description', 'sdate', 'edate', 'price']
        widgets = {
            'sdate': forms.DateInput(attrs={'type': 'date'}),
            'edate': forms.DateInput(attrs={'type': 'date'}),
        }

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

class MakeOrder(ModelForm):
    max_days = 1
    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop('customer', None)
        self.edate = kwargs.pop('edate', None)
        self.sdate = kwargs.pop('sdate', None)
        super().__init__(*args, **kwargs)

        if self.customer:
            self.fields['good'].queryset = Good.objects.filter(
                customer=self.customer,
                status_id=1
            ).order_by('-date')

        if self.sdate and self.edate:
            sdate_str = self.sdate.strftime('%Y-%m-%d') if hasattr(self.sdate, 'strftime') else str(self.sdate)
            edate_str = self.edate.strftime('%Y-%m-%d') if hasattr(self.edate, 'strftime') else str(self.edate)
            start = self.sdate if not isinstance(self.sdate, str) else datetime.strptime(self.sdate, '%Y-%m-%d').date()
            end = self.edate if not isinstance(self.edate, str) else datetime.strptime(self.edate, '%Y-%m-%d').date()
            delta = (end - start).days + 1
            max_days = max(delta, 1)

            self.fields['sdate'].widget.attrs.update({
                'type': 'date',
                'min': sdate_str,
                'max': edate_str,
            })

            DAYS_CHOICES = [(i, str(i)) for i in range(1, max_days + 1)]
            self.fields['days'].choices = DAYS_CHOICES
            self.fields['days'].widget.attrs.update({
                'min': 1,
                'max': max_days,
            })

    days = forms.ChoiceField(
        label="Количество дней",
        choices=[],
        required=True,
    )

    category = forms.ModelChoiceField(
        queryset=GoodCategory.objects.all(),
        label="Категория товара"
    )

    good = forms.ModelChoiceField(
        queryset=Good.objects.none(),
        label="Ваши товары"
    )

    # def clean(self):
    #     cleaned_data = super().clean()
    #     sdate = cleaned_data.get('sdate')
    #     # edate = cleaned_data.get('edate')
    #     if sdate and edate:
    #         if sdate < self.sdate or edate > self.edate:
    #             raise forms.ValidationError('Даты должны быть в диапазоне от {} до {}'.format(self.sdate, self.edate))
    #         if edate < sdate:
    #             raise forms.ValidationError('Дата окончания должна быть не раньше даты начала')
    #     return cleaned_data


    class Meta:
        model = Advertisement
        fields = ['name', 'category', 'good', 'description', 'sdate',  'price', 'days']
        labels = {
            'sdate': 'Выберите дату начала аренды',
        }
        widgets = {
            'sdate': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            # 'edate': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
        }


SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]

class CommentForm(forms.Form):
    score_value = forms.ChoiceField(choices=SCORE_CHOICES, widget=forms.RadioSelect, label='Оценка')
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False, label='Комментарий')
    photo = forms.ImageField(required=False, label='Фотография к комментарию')

    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop('customer')
        self.buyer = kwargs.pop('buyer')
        self.ad = kwargs.pop('ad', None)
        super().__init__(*args, **kwargs)

    def save(self):
        score_val = int(self.cleaned_data['score_value'])

        # Создаем новую оценку
        score_obj = CustomerScore.objects.create(
            score=score_val,
            date=timezone.now().date(),
            customer=self.customer,
            buyer=self.buyer
        )

        # Если комментарий есть, создаем Comment
        comment_text = self.cleaned_data.get('comment')
        photo = self.cleaned_data.get('photo')
        if comment_text or photo:
            Comment.objects.create(
                customer=self.customer,
                buyer=self.buyer,
                ad=self.ad,
                comment=comment_text,
                photo=photo,
                score=score_obj,
                moderate=0
            )

        # Обновляем средний рейтинг пользователя
        avg_rating = CustomerScore.objects.filter(customer=self.customer).aggregate(avg=Avg('score'))['avg']
        print(avg_rating)
        if avg_rating is not None:
            self.customer.rating = round(avg_rating, 2)  # округляем до 2 знаков
            self.customer.save(update_fields=['rating'])

        return score_obj