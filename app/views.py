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


@csrf_exempt
# Create your views here.
def login(req):
    return render(req, 'page-login.html')


def new_patient(req):
    if req.method == 'GET':
        return render(req, 'new-patient.html')
    else:
        print(req.POST)
    '''
    变量名对应的含义
    NPSurname : 新增病人的姓
    NPName : 新增病人的名
    NPEmail : 邮件
    NPPhoneNumber : 手机号
    NPBirth : 出生年月
    NPMarriage, NPGender, NPBloodType 这三个下拉选项的值可以查阅项目中的README文档，其中有记载
    NPWeight : 体重
    NPHeight : 身高
    NPAddress : 地址
    NPCase : 过往病史
    '''


def new_diagnosis(req):
    return render(req, 'new-diagnosis.html')


def upload(req):
    '''
    新增诊断，针对已经存在的患者，这一步还要收集当前的病人信息，将诊断结果给到该病人
    当前这个req不知道有没有这些信息，如果没有的话，后续再处理
    :param req:
    :return:
    '''
    file = req.FILES.get("uploadfile")
    index = 1
    if file is None:
        return render(req, 'new-diagnosis.html', {'error': '请选择zip文件后再识别'})
    else:
        path = default_storage.save('tmp' + '\\' + str(index) + '.zip', ContentFile(file.read()))
        zip_src = sys.path[0] + '\\' + path
        zip_dst = sys.path[0] + '\\' + 'unzip\\test'
        if zipfile.is_zipfile(zip_src) == 0:
            return render(req, 'new-diagnosis.html', {'error': '请选择zip文件后再识别'})
        else:
            unzip_file(zip_src, zip_dst)
            # identy(sys.path[0] + '\\' + 'unzip', sys.path[0] + '\\' + 'result\\' + str(index) + '.json',
            #        sys.path[0] + '\\' + 'IPN\\result_path'
            #                             '\\save_50.pth', sys.path[0] + '\\' + 'IPN')

    return HttpResponse("ok")
    # print(file)



