from django.http import HttpResponse
from django.shortcuts import render
import os
import sys
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from Intelligent_analysis_of_fundus_OCTA_images.tools import unzip_file
from IPN.identify import identy
from django.views.decorators.csrf import csrf_exempt
import zipfile
from app import models

@csrf_exempt
# Create your views here.
def login(req):
    if req.method == 'GET':
        return render(req, 'page-login.html')
    else:
        account = req.POST['account']
        password = req.POST["password"]
        person = models.User.objects.filter(account=account, password=password)
        if person:
            req.session["info"] = {'account': person[0].account,'id': person[0].identity}
            return redirect('/index/')
        else:
            return render(req, 'page-login.html', {'account': account, 'error_msg': '账号或者密码错误'})


def index(req):
    return render(req, 'index.html')

def new_patient(req):
    return render(req, 'new-patient.html')


def upload(req):
    file = req.FILES.get("uploadfile")
    index = 1
    if file is None:
        return render(req, 'new-patient.html', {'error': '请选择zip文件后再识别'})
    else:
        path = default_storage.save('tmp' + '\\' + str(index) + '.zip', ContentFile(file.read()))
        zip_src = sys.path[0] + '\\' + path
        zip_dst = sys.path[0] + '\\' + 'unzip\\test'
        if zipfile.is_zipfile(zip_src) == 0:
            return render(req, 'new-patient.html', {'error': '请选择zip文件后再识别'})
        else:
            unzip_file(zip_src, zip_dst)
            identy(sys.path[0] + '\\' + 'unzip', sys.path[0] + '\\' + 'result\\' + str(index) + '.json',
                   sys.path[0] + '\\' + 'IPN\\result_path'
                                        '\\save_50.pth', sys.path[0] + '\\' + 'IPN')

    return HttpResponse("ok")
    # print(file)
