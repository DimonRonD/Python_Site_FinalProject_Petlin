from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse
from django.db.models import Q, Sum, F
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from .models import Good, City, Advertisement, Order, Customer, CustomerStatus, OrderStatus, OrderStatus, GoodImage, ImageStatus
from .forms import LoginForm, RegisterForm, AddGood, GoodImageFormSet, AddAd, EditAd, EditGood

# Create your views here.

def auth_site(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
                login(request, user)
                redirect_url = reverse("add_good")    # reverse("list_goods")
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

def add_ad(request, good_id):
    customer = request.user
    good = Good.objects.get(id=good_id)
    print(request.POST)
    if request.method == 'POST':
        form = AddAd(request.POST)
        if form.is_valid():
            print('Enter to the Valid')
            ad = form.save(commit=False)  # создаём объект, но не сохраняем в БД
            ad.customer = request.user    # задаём автора объявления
            ad.city = request.user.city   # если требуется, копируем город пользователя
            ad.good = good
            ad.category = good.category
            ad.save()                     # теперь сохраняем в базу
            redirect_url = reverse("list_ads")
            return HttpResponseRedirect(redirect_url)
        else:
            print(form.errors)
    else:
        form = AddAd()

    context = {'form': form,
               'good': good,}
    return render(request, 'add_ad.html', context)

def edit_ad(request, ad_id):
    customer = request.user
    if request.method == 'POST':
        adds = Advertisement.objects.get(id=ad_id)
        adds.name = request.POST.get('name')
        adds.description = request.POST.get('description')
        adds.sdate = request.POST.get('sdate')
        adds.edate = request.POST.get('edate')
        adds.price = request.POST.get('price')
        adds.save()
        redirect_url = reverse("list_ads")
        return HttpResponseRedirect(redirect_url)
    else:
        adds = Advertisement.objects.get(id=ad_id)
        good = adds.good
        form = EditAd(
            customer=customer,
            initial={
                'name': adds.name,
                'category': good.category,  # или конкретный ID
                'good': good,
                'description': adds.description,
                'price': adds.price,
                'sdate': adds.sdate,
                'edate': adds.edate,
            }
        )
        form.fields['category'].disabled = True
        form.fields['good'].disabled = True
    context = {'form': form}
    return render(request, 'edit_ad.html', context)



def add_good(request):
    customer = request.user
    if request.method == 'POST':
        form = AddGood(request.POST,)
        formset = GoodImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            good = form.save(commit=False)
            good.customer = customer
            good = form.save()

            # Сохранение изображений
            for img_form in formset:
                if img_form.cleaned_data.get('image'):  # проверяем наличие файла
                    img = img_form.save(commit=False)
                    img.good = good
                    img.save()

            return redirect('list_ads')  # перенаправляем на страницу со списком товаров
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

def edit_good(request, good_id):
    customer = request.user

    if request.method == 'POST':
        good = Good.objects.get(id=good_id, customer=customer)
        formset = GoodImageFormSet(request.POST, request.FILES, instance=good)
        good.name = request.POST.get('name')
        good.description = request.POST.get('description')
        good.save()
        formset.save()
        redirect_url = reverse("list_goods")
        return HttpResponseRedirect(redirect_url)
    else:
        good = Good.objects.get(id=good_id)
        form = EditGood(
            customer=customer,
            initial={
                'name': good.name,
                'category': good.category,  # или конкретный ID
                'good': good,
                'description': good.description,
                'status': good.status,
            }
        )
        form.fields['category'].disabled = True
        form.fields['good'].disabled = True
        formset = GoodImageFormSet(instance=good)
    context = {'form': form,
               'formset': formset,
               }
    return render(request, 'edit_good.html', context)


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
    goods = Good.objects.filter(customer=customer, status_id=1).order_by('-date', '-id')
    ads = Advertisement.objects.filter(customer=customer).order_by('-sdate')
    context = {'goods': goods,
               'customer': customer,
               'ads': ads,
               }

    return render(request, 'list_ad.html', context)

def delete_ad(request, ad_id):
    customer = request.user
    if request.method == 'POST':
        adds = Advertisement.objects.get(id=ad_id, customer=customer)
        adds.delete()
        redirect_url = reverse("list_ads")
        return HttpResponseRedirect(redirect_url)
    else:
        adds = Advertisement.objects.get(id=ad_id, customer=customer)
        good = adds.good
        form = EditAd(
            customer=customer,
            initial={
                'name': adds.name,
                'category': good.category,  # или конкретный ID
                'good': good,
                'description': adds.description,
                'price': adds.price,
                'sdate': adds.sdate,
                'edate': adds.edate,
            }
        )
        form.fields['category'].disabled = True
        form.fields['good'].disabled = True
    context = {'form': form}
    return render(request, 'delete_ad.html', context)

def delete_good(request, good_id):
    customer = request.user
    if request.method == 'POST':
        good = Good.objects.get(id=good_id, customer=customer)
        img = GoodImage.objects.all().filter(good=good)
        adds = Advertisement.objects.all().filter(good=good, customer=customer)
        if adds: adds.delete()
        if img: img.delete()
        good.delete()
        redirect_url = reverse("list_ads")
        return HttpResponseRedirect(redirect_url)
    else:
        good = Good.objects.get(id=good_id, customer=customer)
        img = GoodImageFormSet(request.POST, request.FILES, instance=good)
        adds = Advertisement.objects.all().filter(good=good, customer=customer)
        form = EditGood(
            customer=customer,
            initial={
                'name': good.name,
                'category': good.category,  # или конкретный ID
                'good': good,
                'description': good.description,
            }
        )
        form.fields['category'].disabled = True
        form.fields['good'].disabled = True
    context = {'form': form}
    return render(request, 'delete_good.html', context)

def moder_good(request):
    customer = request.user

    goods = Good.objects.all().filter(status_id=1, moderate=0).order_by('-date')
    context = {'goods': goods,
               'customer': request.user.id,
               }

    return render(request, 'moderate_good.html', context)

def approve_good(request, good_id):
    customer = request.user

    good = Good.objects.get(id=good_id)
    good.moderate = 1
    good.save()
    goods = Good.objects.all().filter(status_id=1, moderate=0).order_by('-date')
    context = {'goods': goods,
               'customer': request.user.id,
               }

    return render(request, 'moderate_good.html', context)

def disapprove_good(request, good_id):
    customer = request.user

    good = Good.objects.get(id=good_id)
    good.moderate = 2
    good.save()
    goods = Good.objects.all().filter(status_id=1, moderate=0).order_by('-date')
    context = {'goods': goods,
               'customer': request.user.id,
               }

    return render(request, 'moderate_good.html', context)

def moder_ad(request):
    customer = request.user
    goods = Good.objects.all().filter(status_id=1, moderate=1).order_by('-date')
    ads = Advertisement.objects.all().filter(moderate=0).order_by('-sdate')
    context = {'goods': goods,
               'customer': customer,
               'ads': ads,
               }

    return render(request, 'moderate_ad.html', context)

def approve_ad(request, ad_id):
    customer = request.user

    adv = Advertisement.objects.get(id=ad_id)
    adv.moderate = 1
    adv.save()
    goods = Good.objects.all().filter(status_id=1, moderate=1).order_by('-date')
    ads = Advertisement.objects.all().filter(moderate=0).order_by('-sdate')
    context = {'goods': goods,
               'customer': customer,
               'ads': ads,
               }

    return render(request, 'moderate_ad.html', context)

def disapprove_ad(request, ad_id):
    customer = request.user

    adv = Advertisement.objects.get(id=ad_id)
    adv.moderate = 2
    adv.save()
    goods = Good.objects.all().filter(status_id=1, moderate=1).order_by('-date')
    ads = Advertisement.objects.all().filter(moderate=0).order_by('-sdate')
    context = {'goods': goods,
               'customer': customer,
               'ads': ads,
               }

    return render(request, 'moderate_ad.html', context)

