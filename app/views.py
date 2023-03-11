import random
from django.shortcuts import render, redirect, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from Intelligent_analysis_of_fundus_OCTA_images.tools import unzip_file
# from IPN.identify import identy
from django.views.decorators.csrf import csrf_exempt
import zipfile
import sys
from app import models


@csrf_exempt
# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'page-login.html')
    else:
        account = request.POST['account']
        password = request.POST["password"]
        person = models.User.objects.filter(account=account, password=password)
        if person:
            request.session["info"] = {'account': person[0].account, 'id': person[0].identity}
            return redirect('/index/')
        else:
            return render(request, 'page-login.html', {'account': account, 'error_msg': '账号或者密码错误'})


def register(request):
    if request.method == 'GET':
        return render(request, 'page-register.html')
    else:
        content = {'account': request.POST['account'], 'password': request.POST['password']}
        if 'sent_code' in request.POST:
            if models.User.objects.filter(account=content['account']):
                return render(request, 'page-register.html',{'account':"邮箱已注册"})

            vcode = random.randint(1001, 9999)
            print(vcode)
            response = render(request, 'page-register.html',content)
            response.set_cookie('vcode',str(vcode), 60 * 5)
            response.set_cookie('register',content['account'],60*5)
            return response

        if 'new_acc' in request.POST:
            if models.User.objects.filter(content['account']):
                return render(request, 'page-register.html',{'account':"邮箱已注册"})
            if request.COOKIES.get('vcode') == request.POST['in_code']:
                if request.COOKIES.get('register') == request.POST['account']:
                    models.User.objects.create(account=content['account'], password=content['password'], identity=0,
                                               case_number=0)
                return redirect('/index/')
        return render(request, 'page-register.html', content)


def index(req):
    return render(req, 'index.html')


def all_patient(req):
    # 获取当前医生账户名
    account = req.session["info"]['account']
    # 查询获得该医生下病人信息
    case_list = models.Case.objects.filter(case_account=account)

    return render(req, 'all-patients.html', {'case_list': case_list})


def new_patient(req):
    if req.method == 'GET':
        return render(req, 'new-patient.html')

    else:
        print(req.POST)
        # 中间应该添加数据库操作将数据存至数据库中，创建新的病人信息

        # file是图片文件在内存中

        return redirect(new_diagnosis)

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


def new_diagnosis(request):
    if request.method == 'GET':
        return render(request, 'new-diagnosis.html')
    else:
        return


def upload(req):
    """
    新增诊断，针对已经存在的患者，这一步还要收集当前的病人信息，将诊断结果给到该病人
    当前这个req不知道有没有这些信息，如果没有的话，后续再处理
    :param req:
    :return:
    """
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
