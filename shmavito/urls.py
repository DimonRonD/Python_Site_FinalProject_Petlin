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
    path('edit_good/<int:good_id>', views.edit_good, name='edit_good'),
    path('delete_good/<int:good_id>', views.delete_good, name='delete_good'),
    path('add_ad/<int:good_id>', views.add_ad, name='add_ad'),
    path('edit_ad/<int:ad_id>', views.edit_ad, name='edit_ad'),
    path('delete_ad/<int:ad_id>', views.delete_ad, name='delete_ad'),
    path('list_goods', views.list_goods, name='list_goods'),
    path('list_ads', views.list_ads, name='list_ads'),
]