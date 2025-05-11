from django.urls import path
from . import views

urlpatterns = [
    # #При использовании параметров функции-представления, параметры указываются в системе маршрутизации
    path('home/', views.all_in_one, name="home"),
    path('check_worker_progress/', views.check_worker_progress, name="home")
]