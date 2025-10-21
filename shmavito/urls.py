from django.urls import path

from . import views

urlpatterns = [
    path("", views.auth_site),
    path("redirect", views.auth_site, name="redirect"),
    path('register', views.register, name='register'),
    path('add_good', views.add_good, name='add_good'),
]