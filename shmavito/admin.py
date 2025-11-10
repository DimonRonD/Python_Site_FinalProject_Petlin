from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from shmavito.models import GoodCategory, Good, Customer, GoodStatus, Order, OrderStatus, Advertisement, GoodImage, \
    ImageStatus, City, Comment, AdvertisementStatus

# Register your models here.
admin.site.register(GoodCategory)
admin.site.register(Good)
admin.site.register(GoodStatus)
admin.site.register(Customer, UserAdmin)
admin.site.register(Order)
admin.site.register(OrderStatus)
admin.site.register(AdvertisementStatus)
admin.site.register(Advertisement)
admin.site.register(GoodImage)
admin.site.register(ImageStatus)
admin.site.register(City)
admin.site.register(Comment)