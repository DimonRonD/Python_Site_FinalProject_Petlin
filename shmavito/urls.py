from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path

from . import views

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'))),
    path("", views.listing, name="listing"),
    path("redirect", views.listing, name="redirect"),
    path("auth/", views.auth_site, name="auth"),
    path("logout/", views.auth_logout, name="logout"),
    path('register', views.register, name='register'),

    path('add_ad/<int:good_id>', views.add_ad, name='add_ad'),
    path('edit_ad/<int:ad_id>', views.edit_ad, name='edit_ad'),
    path('delete_ad/<int:ad_id>', views.delete_ad, name='delete_ad'),
    path('moder_ad/', views.moder_ad, name='moder_ad'),
    path('approve_ad/<int:ad_id>', views.approve_ad, name='approve_ad'),
    path('disapprove_ad/<int:ad_id>', views.disapprove_ad, name='disapprove_ad'),
    path('list_ads', views.list_ads, name='list_ads'),

    path('listing', views.listing, name='listing'),

    path('add_good', views.add_good, name='add_good'),
    path('edit_good/<int:good_id>', views.edit_good, name='edit_good'),
    path('good/<int:good_id>', views.show_good, name='good'),
    path('delete_good/<int:good_id>', views.delete_good, name='delete_good'),
    path('list_goods', views.list_goods, name='list_goods'),
    path('moder_good/', views.moder_good, name='moder_good'),
    path('approve_good/<int:good_id>', views.approve_good, name='approve_good'),
    path('disapprove_good/<int:good_id>', views.disapprove_good, name='disapprove_good'),

    path('user_page/<int:user_id>', views.user_page, name='user_page'),

    path('make_order/<int:ad_id>', views.make_order, name='make_order'),
    path('my_orders', views.my_orders, name='my_orders'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/', views.order, name='order'),
]