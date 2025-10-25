from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path

from . import views

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'))),
    path("", views.auth_site),
    path("redirect", views.auth_site, name="redirect"),
    path('register', views.register, name='register'),
    path('add_good', views.add_good, name='add_good'),
    path('add_ad/<int:good_id>', views.add_ad, name='add_ad'),
    path('edit_ad/<int:ad_id>', views.edit_ad, name='edit_ad'),
    path('list_goods', views.list_goods, name='list_goods'),
    path('list_ads', views.list_ads, name='list_ads'),
]