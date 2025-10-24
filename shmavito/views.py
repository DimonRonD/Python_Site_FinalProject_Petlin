from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse
from django.db.models import Q, Sum, F
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from .models import Good, City, Advertisement, Order, Customer, CustomerStatus, OrderStatus, OrderStatus, GoodImage, ImageStatus
from .forms import LoginForm, RegisterForm, AddGood, GoodImageFormSet, AddAd

# Create your views here.

def auth_site(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
                login(request, user)
                redirect_url = reverse("add_ad")    # reverse("list_goods")
                return HttpResponseRedirect(redirect_url)
            except Exception as e:
                return HttpResponse(f"Нихера не вышло {e}")
        else:
            return HttpResponse(f"Нихера не вышло")
    else:
        form = LoginForm()
        context = {'form': form,
                   }
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
        form = AddAd(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)  # создаём объект, но не сохраняем в БД
            ad.customer = request.user    # задаём автора объявления
            ad.city = request.user.city   # если требуется, копируем город пользователя
            ad.save()                     # теперь сохраняем в базу
            redirect_url = reverse("list_ad")
            return HttpResponseRedirect(redirect_url)
    else:
        form = AddAd()
    context = {'form': form}
    return render(request, 'add_ad.html', context)

def add_good(request):
    if request.method == 'POST':
        form = AddGood(request.POST)
        formset = GoodImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            # Сохранение основного товара
            good = form.save()

            # Сохранение изображений
            for img_form in formset:
                if img_form.cleaned_data.get('image'):  # проверяем наличие файла
                    img = img_form.save(commit=False)
                    img.good = good  # привязываем изображение к товару
                    img.save()

            return redirect('list_goods')  # перенаправляем на страницу со списком товаров
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


def list_goods(request):
    customer1 = request.user
    goods = Good.objects.all().filter(customer=6, status_id=1).order_by('-date')
    context = {'goods': goods,
               'customer': request.user.id,
               'cuscus': customer1,
               }

    return render(request, 'list_goods.html', context)

def list_ads(request):
    customer = request.user.id
    goods = Good.objects.all().filter(customer=customer, status_id=1).order_by('-date')
    ads = Advertisement.objects.all().filter(customer=customer).order_by('-sdate')
    context = {'goods': goods,
               'customer': customer,
               'ads': ads,
               }

    return render(request, 'list_ad.html', context)