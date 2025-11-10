import copy
from datetime import datetime, timedelta

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.db.models import Q, Sum, F, Exists, OuterRef
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from .models import Good, City, Advertisement, Order, Customer, CustomerStatus, OrderStatus, OrderStatus, GoodImage, \
    ImageStatus, AdvertisementStatus
from .forms import LoginForm, RegisterForm, AddGood, GoodImageFormSet, AddAd, EditAd, EditGood, MakeOrder


# Create your views here.

def auth_site(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
                login(request, user)
                print(user)
                redirect_url = reverse("listing")    # reverse("list_goods")
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

def auth_logout(request):
    logout(request)
    return redirect('redirect')

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
        adds.moderate = 0
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
        good.moderate = 0
        good.save()
        formset.save()
        redirect_url = reverse("list_ads")
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
    customer = request.user
    goods = Good.objects.all().filter(customer=customer).order_by('-date')
    context = {'goods': goods,
               'customer': customer,
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

def listing(request):
    if request.user.is_authenticated:
        customer = request.user
        ads_subquery = Advertisement.objects.filter(moderate=1, status=1, good=OuterRef('pk'))

        goods = Good.objects.annotate(
            has_ads=Exists(ads_subquery)
        ).filter(
            status_id=1,
            moderate=1,
            has_ads=True
        ).order_by('-date', '-id')

        ads = Advertisement.objects.filter(moderate=1, status=1, good__in=goods).order_by('-sdate')
        context = {'goods': goods,
                   'customer': customer,
                   'ads': ads,
                   }
        return render(request, 'list_all.html', context)
    else:
        ads_subquery = Advertisement.objects.filter(moderate=1, good=OuterRef('pk'))

        goods = Good.objects.annotate(
            has_ads=Exists(ads_subquery)
        ).filter(
            status_id=1,
            moderate=1,
            has_ads=True
        ).order_by('-date', '-id')

        ads = Advertisement.objects.filter(moderate=1, good__in=goods).order_by('-sdate')
        context = {'goods': goods,
                   'ads': ads,
                   }

        return render(request, 'list_anon.html', context)

def user_page(request, user_id):
    user_name = Customer.objects.get(id=user_id)
    print(user_name)
    ads_subquery = Advertisement.objects.filter(moderate=1, customer=user_id, good=OuterRef('pk'))

    goods = Good.objects.annotate(
        has_ads=Exists(ads_subquery)
    ).filter(
        status_id=1,
        moderate=1,
        customer=user_id,
        has_ads=True
    ).order_by('-date', '-id')

    ads = Advertisement.objects.filter(moderate=1, customer=user_id, good__in=goods).order_by('-sdate')
    context = {'goods': goods,
               'user_name': user_name,
               'ads': ads,
               }

    return render(request, 'user_page.html', context)

def make_order(request, ad_id):

    customer = request.user
    if request.method == 'POST':
        adds = Advertisement.objects.get(id=ad_id)
        order_sdate = datetime.strptime(request.POST.get('sdate'), "%Y-%m-%d").date()
        order_days = int(request.POST.get('days'))
        order_days_for_date = order_days - 1                    # надо уменьшать на один день, так как стартовая дата уже один день
        calculated_edate = order_sdate + timedelta(days=order_days_for_date)
        if calculated_edate > adds.edate:
            redirect_url = reverse("make_order", args=[ad_id])
            error_msg = 'Вы выбрали количество дней, превышающее срок аренды'
            context = {'error': error_msg}
            return HttpResponseRedirect(redirect_url)
        order_status = OrderStatus.objects.get(id=1)
        order = Order.objects.create(
            ad = adds,
            customer = customer,
            order_date = datetime.now(),
            sdate = order_sdate,
            edate = calculated_edate,
            status = order_status,
            price = adds.price * order_days
        )
        if order_sdate == adds.sdate and calculated_edate == adds.edate:
            adds.status = AdvertisementStatus.objects.get(id=2)
            adds.save()
            redirect_url = reverse("my_orders")
            return HttpResponseRedirect(redirect_url)
        elif order_sdate > adds.sdate:                        # Если дата начала заказа  больше даты начала предложения
            adds_copy = copy.copy(adds)
            adds_copy.pk = None
            adds_copy.edate = order_sdate - timedelta(days=1) # Дата начала предложения сохраняется, дата конца предложения = дата начала заказа - 1 день
            adds_copy.save()
            if calculated_edate < adds.edate:                   # Если дата конца заказа меньше даты конца предложения
                adds_copy2 = copy.copy(adds)
                adds_copy2.pk = None
                adds_copy2.sdate = calculated_edate + timedelta(days=1) # Дата начала нового предложения равна дата конца заказа + 1 день
                adds_copy2.save()
            adds.status = AdvertisementStatus.objects.get(id=3)
            adds.save()
            redirect_url = reverse("my_orders")
            return HttpResponseRedirect(redirect_url)
        elif order_sdate == adds.sdate and calculated_edate < adds.edate:   # Если дата начала заказа равна дате начала предложения и дата конца заказа меньше даты конца предложения
            adds_copy3 = copy.copy(adds)
            adds_copy3.pk = None
            adds_copy3.sdate = calculated_edate + timedelta(days=1)   # дата начала предложения равна дате конца заказа + 1 день
            adds_copy3.save()
            adds.status = AdvertisementStatus.objects.get(id=3)
            adds.save()
            redirect_url = reverse("my_orders")
            return HttpResponseRedirect(redirect_url)
        return HttpResponse(f"Что-то не так с датами<br> sdate: {adds.sdate} edate: {adds.edate}<br> order_sdate: {order_sdate} calculated_edate: {calculated_edate}<br> days: {order_days}")
    else:
        adds = Advertisement.objects.get(id=ad_id)
        good = adds.good
        form = MakeOrder(
            customer=customer,
            sdate=adds.sdate,
            edate=adds.edate,
            initial={
                'name': adds.name,
                'category': good.category,  # или конкретный ID
                'good': good,
                'description': adds.description,
                'price': adds.price,
                'sdate': adds.sdate,
            }
        )
        form.fields['name'].disabled = True
        form.fields['category'].disabled = True
        form.fields['good'].disabled = True
        form.fields['description'].disabled = True
        form.fields['price'].disabled = True

        context = {'goods': good,
                   'ads': adds,
                   'form': form,
                   }
        return render(request, 'make_order.html', context)

def my_orders(request):
    customer = request.user
    orders = Order.objects.all().filter(customer=customer).order_by('-order_date')
    # advs = Advertisement.objects.all().filter(customer=customer)
    # goods = Good.objects.all().filter(customer=customer)
    adv_ids = orders.values_list('ad_id', flat=True).distinct()
    advs = Advertisement.objects.filter(id__in=adv_ids)

    good_ids = advs.values_list('good_id', flat=True).distinct()
    goods = Good.objects.filter(id__in=good_ids)

    context = {'goods': goods,
               'customer': customer,
               'orders': orders,
               'advs': advs,
               }

    return render(request, 'my_orders.html', context)