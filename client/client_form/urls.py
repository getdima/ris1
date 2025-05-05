from django.urls import path
from . import views

urlpatterns = [
    # #При использовании параметров функции-представления, параметры указываются в системе маршрутизации
    path('home/', views.index, name="home"),
    path('make_request/', views.make_request),
    path('check_request_status/', views.check_request_status),
    path('request_status/', views.request_status),
    path('check_worker_progress/', views.check_worker_progress)
]