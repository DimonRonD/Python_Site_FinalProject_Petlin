FROM python:3.13
LABEL authors="dmitriipetlin"

WORKDIR /shmavito
COPY requirements.txt /shmavito
RUN pip install -r requirements.txt

COPY . /shmavito

RUN python manage.py makemigrations

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.settings

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]