from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomerStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название статуса')

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='Город')

    def __str__(self):
        return self.name

class Customer(AbstractUser):
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='customers', verbose_name='Город')
    phone = models.CharField(max_length=15, verbose_name='Номер телефона')
    tg_name = models.CharField(max_length=50, verbose_name='Имя пользователя Telegram', null=True)
    tg_id = models.IntegerField(verbose_name='ID в Telegram', null=True)
    status = models.ForeignKey(CustomerStatus, on_delete=models.PROTECT, related_name='customers', verbose_name='Статус пользователя', default=1)

class GoodCategory(models.Model):
    name = models.CharField(max_length=25, verbose_name='Категория товара', default='Одежда')

    def __str__(self):
        return self.name

class GoodStatus(models.Model):
    name = models.CharField(max_length=25, verbose_name='Статус товара')

    def __str__(self):
        return self.name

class Good(models.Model):
    name = models.CharField(max_length=250, verbose_name='Название товара')
    category = models.ForeignKey(GoodCategory, on_delete=models.PROTECT, related_name='good', verbose_name='Категория товара')
    description = models.TextField(verbose_name='Описание товара')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='good')
    date = models.DateField(verbose_name='Дата создания товара', auto_now=True)
    status = models.ForeignKey(GoodStatus, on_delete=models.PROTECT, related_name='good', default=1, verbose_name='Статус товара')

    def __str__(self):
        return self.name

class ImageStatus(models.Model):
    name = models.CharField(max_length=25, verbose_name='Статус фотографии')

    def __str__(self):
        return self.name

class GoodImage(models.Model):
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField(verbose_name='Фотография товара')
    status =models.ForeignKey(ImageStatus, on_delete=models.PROTECT, related_name='images', default=1, verbose_name='Статус фотографии')

class Advertisement(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='adv', verbose_name='Пользователь')
    good = models.ForeignKey(Good, on_delete=models.PROTECT, related_name='adv', verbose_name='Товар')
    sdate = models.DateField(verbose_name='Дата начала предложения')
    edate = models.DateField(verbose_name='Дата окончания предложения')
    name = models.CharField(max_length=200, verbose_name='Название предложения')
    description = models.TextField(verbose_name='Описание предложения')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость одного дня предложения')
    moderate = models.BooleanField(default=False, verbose_name='Прошел модерацию')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='adv', verbose_name='Город')

class OrderStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name='Статус предложения')

    def __str__(self):
        return self.name

class Order(models.Model):
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='orders', verbose_name='Предложение')
    order_date = models.DateField(verbose_name='Дата заказа')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, related_name='orders', verbose_name='Статус заказа')
    sdate = models.DateField(verbose_name='Дата начала заказа')
    edate = models.DateField(verbose_name='Дата окончания заказа')

class Comment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='comments', verbose_name='Пользователь')
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='comments', null=True, verbose_name='Предложение')
    comment = models.TextField(null = False, verbose_name='Комментарий')
    photo = models.ImageField(null=True, verbose_name='Фотография к комментарию')

