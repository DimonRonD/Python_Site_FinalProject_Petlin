import copy
from datetime import datetime, timedelta
from itertools import zip_longest
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.db.models import Q, Sum, F, Exists, OuterRef
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from .models import Good, City, Advertisement, Order, Customer, CustomerStatus, OrderStatus, OrderStatus, GoodImage, \
    ImageStatus, AdvertisementStatus, Comment
from .forms import LoginForm, RegisterForm, AddGood, GoodImageFormSet, AddAd, EditAd, EditGood, MakeOrder, CommentForm, AdvertisementSearchForm


# Create your views here.

def auth_site(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
                login(request, user)
                customer = Customer.objects.get(username=email)
                if customer.isModerator:
                    return render(request, 'moderate_ad.html')
                else:
                    redirect_url = reverse("listing")
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
    if request.method == 'POST':
        form = AddAd(request.POST)
        if form.is_valid():
            if form.cleaned_data["sdate"] >= form.cleaned_data["edate"]:
                msg = 'Дата начала предложения должна быть меньше даты конца предложения'
                context = {'form': form,
                           'good': good,
                           'msg': msg,
                           }
                return render(request, 'add_ad.html', context)
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
    ads = Advertisement.objects.filter(customer=customer, status=1).order_by('-sdate')
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

def chunked(iterable, n):
    args = [iter(iterable)] * n
    return list(zip_longest(*args, fillvalue=None))

def user_page(request, user_id):
    user_name = Customer.objects.get(id=user_id)
    ads_subquery = Advertisement.objects.filter(moderate=1, customer=user_id, good=OuterRef('pk'))
    comments = Comment.objects.filter(customer=user_id)
    goods = Good.objects.annotate(
        has_ads=Exists(ads_subquery)
    ).filter(
        status_id=1,
        moderate=1,
        customer=user_id,
        has_ads=True
    ).order_by('-date', '-id')
    grouped_ads_by_good = {}
    for good in goods:
        ads = Advertisement.objects.filter(moderate=1, customer=user_id, status=1, good=good).order_by('-sdate')
        ads_list = list(ads)
        ads_grouped = chunked(ads_list, 2)
        grouped_ads_by_good[good] = ads_grouped

    context = {'goods': goods,
               'user_name': user_name,
               'grouped_ads_by_good': grouped_ads_by_good,
               'comments': comments,
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
    orders = Order.objects.all().filter(customer=customer, status=1).order_by('-order_date')
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

def cancel_order(request, order_id):
    pass

def order(request, order_id):
    customer = request.user
    order = Order.objects.get(customer=customer, id=order_id)
    adv = Advertisement.objects.get(id=order.ad.id)
    good = Good.objects.get(id=adv.good.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES, customer=good.customer, buyer=customer, good=good)
        if form.is_valid():
            form.save()
            # Делайте перенаправление или нужный ответ
    else:
        comments = Comment.objects.filter(good=good, buyer=customer).order_by('-date')
        all_comments = Comment.objects.filter(good=good).order_by('-date')
        if comments:
            context = {'good': good,
                       'customer': customer,
                       'order': order,
                       'already_commented': 'True',
                       'comments': comments,
                       'all_comments': all_comments,
                       }
        else:
            form = CommentForm(customer=good.customer, buyer=customer, good=good)
            context = {'good': good,
                       'customer': customer,
                       'order': order,
                       'form': form,
                       'already_commented': 'False',
                       'all_comments': all_comments,
                       }

    return render(request, 'order.html', context)

def comment(request, order_id):
    customer = request.user
    buyer = Customer.objects.get(id=buyer_id)
    ad = Advertisement.objects.get(id=ad_id) if ad_id else None

    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES, customer=customer, buyer=buyer, ad=ad)
        if form.is_valid():
            form.save()
            # Делайте перенаправление или нужный ответ
    else:
        form = CommentForm(customer=customer, buyer=buyer, ad=ad)

    return render(request, 'your_template.html', {'form': form})


def listing(request):
    if request.user.is_authenticated:
        customer = request.user
    else:
        customer = None

    form = AdvertisementSearchForm(request.GET or None)

    ads_subquery = Advertisement.objects.filter(moderate=1, status=1, good=OuterRef('pk'))
    goods = Good.objects.annotate(has_ads=Exists(ads_subquery)).filter(
        status_id=1, moderate=1, has_ads=True
    )
    ads = Advertisement.objects.filter(moderate=1, status=1, good__in=goods)

    # Получаем значения полей формы
    keyword = form.data.get('keyword')
    city = form.data.get('city')
    price_min = form.data.get('price_min')
    price_max = form.data.get('price_max')
    category = form.data.get('category')

    # Проверка: хотя бы одно поле непустое
    if any([
        keyword and keyword.strip(),
        city and city != '',
        price_min and price_min != '',
        price_max and price_max != '',
        category and category != '',
    ]):
        if form.is_valid():
            keyword = form.cleaned_data.get('keyword')
            city = form.cleaned_data.get('city')
            price_min = form.cleaned_data.get('price_min')
            price_max = form.cleaned_data.get('price_max')
            category = form.cleaned_data.get('category')

            filter_qs = Q()
            good_filter = Q()

            # Поиск по Good (имя, описание, категория)
            if keyword:
                good_filter |= Q(name__icontains=keyword) | Q(description__icontains=keyword)
            if category:
                good_filter &= Q(category=category)

            # ids товаров, подходящих по имени, описанию, категории
            matched_good_ids = Good.objects.filter(good_filter).values_list('id', flat=True) if (keyword or category) else None

            # Поиск по Advertisement (заголовок, описание + товары)
            if matched_good_ids is not None:
                filter_qs |= Q(good_id__in=matched_good_ids)
            if keyword:
                filter_qs |= Q(name__icontains=keyword) | Q(description__icontains=keyword)
            if city:
                filter_qs &= Q(city=city)
            if price_min is not None:
                filter_qs &= Q(price__gte=price_min)
            if price_max is not None:
                filter_qs &= Q(price__lte=price_max)

            ads = ads.filter(filter_qs)
            filtered_good_ids = ads.values_list('good_id', flat=True)
            goods = goods.filter(id__in=filtered_good_ids)

    ads = ads.order_by('-sdate')
    goods = goods.order_by('-date', '-id')

    context = {
        'goods': goods,
        'ads': ads,
        'customer': customer,
        'form': form,
    }

    template_name = 'list_all.html' if request.user.is_authenticated else 'list_anon.html'
    return render(request, template_name, context)

def show_good(request, good_id):
    customer = request.user
    good = Good.objects.get(id=good_id)
    images = GoodImage.objects.filter(good=good)
    comments = Comment.objects.filter(good=good).order_by('-date')
    context = {
        'customer': customer,
        'good': good,
        'images': images,
        'comments': comments,
    }
    return render(request, 'good.html', context)

def cancel_order(request, order_id):
    customer = request.user
    order = Order.objects.get(customer=customer, id=order_id)
    adv = Advertisement.objects.get(id=order.ad.id)
    good = Good.objects.get(id=adv.good.id)

    if request.method == "POST" and request.POST.get('confirm') == 'yes':
        all_advs = Advertisement.objects.filter(good=good, status_id=1).exclude(id=adv.id)

        # Соседние предложения: по датам именно +1/-1 день, чтобы найти только "крайние" блоки
        prev_advs = all_advs.filter(edate=order.sdate - timedelta(days=1))
        next_advs = all_advs.filter(sdate=order.edate + timedelta(days=1))

        # Если есть хоть один сосед, делаем слияние
        if prev_advs.exists() or next_advs.exists():
            # Собираем диапазон
            to_merge = list(prev_advs) + [adv] + list(next_advs)
            new_sdate = min(a.sdate for a in to_merge)
            new_edate = max(a.edate for a in to_merge)

            # Создаём объединённое предложение
            merged_adv = Advertisement.objects.create(
                customer=adv.customer,
                good=good,
                sdate=new_sdate,
                edate=new_edate,
                name=adv.name,
                description=adv.description,
                price=adv.price,
                moderate=1,
                city=adv.city,
                status_id=1,
            )

            # Переводим только участвовавшие предложения (prev_advs и next_advs) в статус 4
            to_update_ids = [a.id for a in prev_advs] + [a.id for a in next_advs]
            if to_update_ids:
                Advertisement.objects.filter(id__in=to_update_ids, status_id=1).update(status_id=4)
                updated = Advertisement.objects.filter(id__in=to_update_ids)
        else:
            # Нет соседей: просто создаём новое предложение, архивируем adv
            Advertisement.objects.create(
                customer=adv.customer,
                good=good,
                sdate=adv.sdate,
                edate=adv.edate,
                name=adv.name,
                description=adv.description,
                price=adv.price,
                moderate=1,
                city=adv.city,
                status_id=1,
            )

        # Заказу статус "отменён"
        order.status_id = 3
        order.save()
        return redirect('my_orders')

    context = {
        'order': order,
        'adv': adv,
        'good': good,
    }
    return render(request, 'cancel_order.html', context)