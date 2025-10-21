from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.db.models import Q, Sum, F
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login

from .models import Good, City, Advertisement, Order, Customer, CustomerStatus, OrderStatus, OrderStatus, GoodImage, ImageStatus
from .forms import LoginForm, RegisterForm, AddGood, GoodImageFormSet

# Create your views here.

def auth_site(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
                login(request, user)
                redirect_url = reverse("goods_list")
                return HttpResponseRedirect(redirect_url)
            except Exception as e:
                return HttpResponse(f"Нихера не вышло {e}")
        else:
            return HttpResponse(f"Нихера не вышло")
    else:
        form = LoginForm()
        context = {'form': form}
        return render(request, 'auth.html', context)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
        redirect_url = reverse("redirect")
        return HttpResponseRedirect(redirect_url)
    else:
        form = RegisterForm()
        context = {'form': form}
        return render(request, 'register.html', context)

def add_ad(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
        redirect_url = reverse("redirect")
        return HttpResponseRedirect(redirect_url)
    else:
        form = RegisterForm()
        context = {'form': form}
        return render(request, 'register.html', context)

def add_good(request):
    if request.method == 'POST':
        form = AddGood(request.POST)
        formset = GoodImageFormSet(request.POST, request.FILES)
        print('Мы во вьюхе')
        if form.is_valid() and formset.is_valid():
            # Сохранение основного товара
            print('Форма валидная и формсет валидный')
            good = form.save()

            # Сохранение изображений
            for img_form in formset:
                if img_form.cleaned_data.get('image'):  # проверяем наличие файла
                    img = img_form.save(commit=False)
                    img.good = good  # привязываем изображение к товару
                    img.save()

            return redirect('goods-list')  # перенаправляем на страницу со списком товаров
        else:
            errors = []  # Проверяем на ошибки при заполнении формы
            if not form.is_valid():
                errors.append(f"Форма товара: {form.errors}")
            if not formset.is_valid():
                errors.append(f"Формы изображений: {formset.non_form_errors()} {formset.errors}")

            print(errors)  # Логируем ошибки
            return HttpResponse("Ошибки при заполнении формы.<br>" + "<br>".join(errors))
    else:
        form = AddGood()
        formset = GoodImageFormSet()

    return render(request, 'add_good.html', {'form': form, 'formset': formset})