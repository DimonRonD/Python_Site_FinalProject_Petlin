Дипломный проект: Веб-сайт для аренды одежды Shmavito

Имя Фамилия: Дмитрий Петлин

логин на GitHub — DimonRonD

e-mail — DimonRonD@gmail.com

docker-compose up shmavito_db - для запуска контейнера с базой

docker-compose up shmavito_web - для запуска web-сервера

Выгрузка данных из базы: python manage.py dumpdata > data.json
Загрузка данных в базу: python manage.py loaddata data.json

python manage.py dumpdata shmavito.CustomerStatus >> data.json
python manage.py dumpdata shmavito.City >> data.json
python manage.py dumpdata shmavito.GoodStatus >> data.json
python manage.py dumpdata shmavito.ImageStatus >> data.json
python manage.py dumpdata shmavito.AdvertisementStatus >> data.json
python manage.py dumpdata shmavito.OrderStatus >> data.json

- [X] Схема базы, создание моделей
- [X] Создание, редактирование, удаление товара
- [X] Создание, редактирование, удаление предложения
- [X] Шаблоны base и header, css, favicon
- [X] Страница просмотра и управления своими заказами и предложениями
- [X] Регистрация, авторизация
- [X] Поиск
- [X] Вход для модератора
- [X] Страница модерации товара
- [X] Страница модерации предложения
- [X] Страница комментариев (профиль пользователя (есть), страница товара (есть))
- [X] Профиль пользователя
- [X] Рейтинг пользователя
- [X] Страница просмотра предложений для авторизованноего пользователя
- [X] Страница просмотра предложений для всех
- [X] Страница создания заказа, разделение дат предложения на два предложения
- [X] Страница "Мои заказы"
- [X] Страница заказа
- [X] Отмена заказа, возврат дат предложению
- [ ] На странице всех товаров сделать разбиение предложений на колонки


Условные обозначения:

[ ] - пункт пока не выполнен

[X] - пункт выполнен

[/] - пункт выполнен частично (надо будет вернуться и дополнить после выполнения других пунктов)
