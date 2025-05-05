import logging
import sys

from django.shortcuts import render
from django.template.response import TemplateResponse

import requests

from . import forms

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect

#При использовании параметров строки запроса, они получаются внутри функции-представления с помощью метода request.GET.get()
# def user(request):
#     id = request.GET.get("id", 10)
#     user_name = request.GET.get("user_name", "Tom")
#     #Названия переменных в данном словаре должны соответствовать названиям переменных в шаблоне
#     data = {"user_name": user_name, "user_id": id}
#     return TemplateResponse(request, "user.html", data)

# Вернет текст "Hello World"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def index(request):
    return TemplateResponse(request, "index.html")

def make_request(request):
    if request.method == "POST":
        req_hash = request.POST.get("hash")
        req_lenght = request.POST.get("maxLength")

        params = {
            "hash" : req_hash,
            "maxLength" : req_lenght
        }

        # print("Сообщение в консоль", file=sys.stderr)

        response = requests.post("http://manager:8080/api/hash/crack", json=params)  
        
        response = response.json()
        
        if (response['error_code'] != "") :
            data = {
                "header" : response['error_message'],
                "body" : "Не получилось создать запрос"
            }
        else :
            data = {
                "header" : "Запрос создан успешно",
                "body" : "Ваш запрос: " + response['request_id']
            }

        return TemplateResponse(request, "request_status.html", data)
    else:
        data = {"form": forms.RequestForm()}
        return TemplateResponse(request, "make_request.html", data)
    
def check_request_status(request):
    if request.method == "POST":
        request_id = request.POST.get("request")
        
        params = {
            'request_id': request_id
        }

        response = requests.get("http://manager:8080/api/hash/status", params=params)

        response = response.json()

        if (response['error_code'] != "") :
            data = {
                "header" : response['error_message'],
            }
        else :
            data = {
                "header" : "Ваш запрос: " + request_id,
                "body" : "Cтатус: " + response['status'],
            }

            if (response['result'] != None):
                data['result'] = "Результат:" + response['result']

        return TemplateResponse(request, "request_status.html", data)
    else:
        data = {"form": forms.RequestStatusForm()}
        return TemplateResponse(request, "check_request_status.html", data)
    
def request_status(request):
    data = request.GET.get("response")
    return TemplateResponse(request, "request_status.html", data)

def check_worker_progress(request):
    if request.method == "POST":
        worker = request.POST.get("worker")
        
        params = {
            'worker': worker
        }

        response = requests.get("http://manager:8080/workerProgress", params=params)

        response = response.json()

        if (response['error_code'] != "") :
            data = {
                "header" : response['error_message'],
            }
        else :
            data = {
                "header" : "Прогресс воркера под индексом " + worker,
                "body" : response['data'],
            }

        return TemplateResponse(request, "request_status.html", data)
    else:
        data = {"form": forms.WorkerProgressForm()}
        return TemplateResponse(request, "check_worker_progress.html", data)