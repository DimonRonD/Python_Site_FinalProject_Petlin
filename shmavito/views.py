from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.db.models import Q, Sum, F
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login

from .models import Good, City, Advertisement, Order, Customer, CustomerStatus, OrderStatus, OrderStatus, GoodImage, ImageStatus
from .forms import LoginForm, RegisterForm

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
