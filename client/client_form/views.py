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

def check_worker_progress(request):
    response = requests.get("http://manager:8080/workerProgress")

    response = response.json()

    if (response['error_code'] != "") :
        data = {
            "header" : response['error_message'],
        }
    else :
        data = {
            "header" : "Текущий статус воркеров",
            "progress" : response['data']
        }
    
    data["create_form"] = forms.RequestForm()
    data["check_form"] = forms.RequestStatusForm()

    return HttpResponseRedirect(f"/crackhash/home/", data)

def all_in_one(request):
    if request.method == "POST":
        if 'create_request' in request.POST:
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

            data["create_form"] = forms.RequestForm()
            data["check_form"] = forms.RequestStatusForm()

            return TemplateResponse(request, "index_all_in_one.html", data)
        elif 'check_status' in request.POST:
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

            data["create_form"] = forms.RequestForm()
            data["check_form"] = forms.RequestStatusForm()

            return TemplateResponse(request, "index_all_in_one.html", data)
        elif 'check_workers' in request.POST:
            response = requests.get("http://manager:8080/workerProgress")

            response = response.json()

            if (response['error_code'] != "") :
                data = {
                    "header" : response['error_message'],
                }
            else :
                data = {
                    "header" : "Текущий статус воркеров",
                    "progress" : response['data']
                }
            
            data["create_form"] = forms.RequestForm()
            data["check_form"] = forms.RequestStatusForm()

            return TemplateResponse(request, "index_all_in_one.html", data)
    else:
        data = {
            "create_form": forms.RequestForm(), 
            "check_form": forms.RequestStatusForm()
        }
        return TemplateResponse(request, "index_all_in_one.html", data)