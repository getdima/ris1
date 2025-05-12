from django.urls import path
from . import views

urlpatterns = [
    # #При использовании параметров функции-представления, параметры указываются в системе маршрутизации
    path('home/', views.all_in_one, name="home"),
]