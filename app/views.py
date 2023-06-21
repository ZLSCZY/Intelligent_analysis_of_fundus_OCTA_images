import json
import random
from django.shortcuts import render, redirect, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from Intelligent_analysis_of_fundus_OCTA_images.tools import unzip_file
from django.core.mail import send_mail
from django.conf import settings
from IPN.identify import identy
from django.views.decorators.csrf import csrf_exempt
import zipfile
import sys
from app import models
from datetime import datetime
from decimal import Decimal
from Heatmap.grad_cam import generator_heatmap

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
                return render(request, 'page-register.html', {'account': "邮箱已注册"})

            vcode = random.randint(1001, 9999)
            send_mail('网址注册验证',
                      '验证码:'+str(vcode),
                      settings.EMAIL_HOST_USER,  # 这里可以同时发给多个收件人
                      ['2025575181@qq.com',content['account']],
                      fail_silently=False)

            response = render(request, 'page-register.html', content)
            response.set_cookie('vcode', str(vcode), 60 * 5)
            response.set_cookie('register', content['account'], 60 * 5)
            return response

        if 'new_acc' in request.POST:
            if models.User.objects.filter(content['account']):
                return render(request, 'page-register.html', {'account': "邮箱已注册"})
            if request.COOKIES.get('vcode') == request.POST['in_code']:
                if request.COOKIES.get('register') == request.POST['account']:
                    models.User.objects.create(account=content['account'], password=content['password'], identity=0,
                                               case_number=0)
                return redirect('/index/')
        return render(request, 'page-register.html', content)


def index(req):
    return render(req, 'index.html')


def all_patient(request):
    # 获取当前医生账户名
    account = request.session["info"]['account']
    # 查询获得该医生下病人信息
    case_list = models.Case.objects.filter(case_account=account)
    # 判断页面跳转的方式
    request.session["from_new_patient"] = False
    # 当前保存的id是否有效
    request.session["id_valid"] = False

    return render(request, 'all-patients.html', {'case_list': case_list})

def del_patient(request):
    models.Case.objects.get(id=request.GET['id']).delete()
    return redirect(all_patient)

def new_patient(request):
    if request.method == 'GET':
        return render(request, 'new-patient.html')

    else:

        # 中间应该添加数据库操作将数据存至数据库中，创建新的病人信息
        user = models.User.objects.filter(account=request.session["info"]['account'])[0]

        np = models.Case.objects.create(case_account=user,
                                        case_number=request.POST['NPNum'],
                                        case_name=request.POST['NPName'],
                                        case_age=request.POST['NPAge'],
                                        case_sex=request.POST['NPGender'],
                                        case_height=request.POST['NPHeight'],
                                        case_weight=request.POST['NPWeight'],
                                        case_blood_type=request.POST['NPBloodType'],
                                        case_history=request.POST['NPCase'],
                                        case_note=request.POST['NPNote'])
        # 存储当前病例在数据库中的主键id
        request.session["curr_case_id"] = {'id': np.id}
        request.session["from_new_patient"] = True
        request.session["id_valid"] = True

        # file是图片文件在内存中

        return redirect(all_patient)

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


# def new_diagnosis(request):
#     if request.method == 'GET':
#         return render(request, 'new-diagnosis.html')
#     else:
#         return


def results(request):
    # 类似于诊断，先获取当前病例id
    curr_case_id = request.GET.get('curr_case_id')
    records = models.QueryRecord.objects.filter(case_id=curr_case_id)
    result = {'AMD': 0, 'DR': 0, 'NORMAL': 0}


    if len(records) == 0:
        result = {'AMD': 'None', 'DR': 'None', 'NORMAL': 'None'}
    else:
        pic_index = records[len(records)-1].qr_pc_id
        for i in records:
            result['AMD'] += float(i.AMD)
            result['DR'] += float(i.DR)
            result['NORMAL'] += float(i.NORMAL)
        result['AMD'] /= len(records)
        result['AMD'] = Decimal(result['AMD']).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
        result['DR'] /= len(records)
        result['DR'] = Decimal(result['DR']).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
        result['NORMAL'] /= len(records)
        result['NORMAL'] = Decimal(result['NORMAL']).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")

    return render(request, 'results.html', {'records': records, 'result': result,
                                            'pic1': '../static/heatmaps/' + pic_index + '-1.png',
                                            'pic2': '../static/heatmaps/' + pic_index + '-2.png',
                                            'pic3': '../static/heatmaps/' + pic_index + '-3.png'})


def upload(request):
    """
    新增诊断，针对已经存在的患者，这一步还要收集当前的病人信息，将诊断结果给到该病人
    当前这个req不知道有没有这些信息，如果没有的话，后续再处理
    :param request:
    :return:
    """

    file = request.FILES.get("uploadfile")
    # index为该病例在数据库中的主键，所有相关文件夹都会以此命名
    # 通过curr_case_id查询表Query_Record得到当前次数

    if not request.session["from_new_patient"]:
        if not request.session["id_valid"]:
            request.session["curr_case_id"] = {'id': request.GET.get('curr_case_id')}
            request.session["id_valid"] = True

    curr_case_id = request.session["curr_case_id"]['id']

    times = len(models.QueryRecord.objects.filter(case_id=curr_case_id)) + 1

    index = str(curr_case_id) + '-' + str(times)
    if file is None:
        return render(request, 'new-diagnosis.html', {'error': '请选择zip文件后再识别'})
    else:
        path = default_storage.save('tmp' + '\\' + str(index) + '.zip', ContentFile(file.read()))
        zip_src = sys.path[0] + '\\' + path
        zip_dst = sys.path[0] + '\\' + 'unzip\\test'
        if zipfile.is_zipfile(zip_src) == 0:
            return render(request, 'new-diagnosis.html', {'error': '请选择zip文件后再识别'})
        else:
            unzip_file(zip_src, zip_dst, index)
            identy(sys.path[0] + '\\' + 'unzip', sys.path[0] + '\\' + 'result\\' + str(index) + '.json',
                   sys.path[0] + '\\' + 'IPN\\result_path'
                                        '\\save_50.pth', sys.path[0] + '\\' + 'IPN', index)
            json_path = sys.path[0] + '\\' + 'result\\' + str(index) + '.json'


            # 保存该次诊断记录
            with open(json_path) as f:
                record_dict = json.load(f)
            qr = models.QueryRecord()
            qr.qr_pc_id = index
            qr.case_id = curr_case_id
            for i in record_dict['results'][index]:
                if i['label'] == 'AMD':
                    qr.AMD = Decimal(i['score']).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
                elif i['label'] == 'NORMAL':
                    qr.NORMAL = Decimal(i['score']).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
                elif i['label'] == 'DR':
                    qr.DR = Decimal(i['score']).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
            qr.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            qr.save()

            generator_heatmap(1, zip_dst + '\\' + index + '\\25.jpg', index + '-1')
            generator_heatmap(2, zip_dst + '\\' + index + '\\50.jpg', index + '-2')
            generator_heatmap(3, zip_dst + '\\' + index + '\\75.jpg', index + '-3')




    return redirect(all_patient)
    # print(file)


def update_patient(request):
    case = models.Case.objects.get(id=request.GET['id'])
    case.case_name = request.GET['NPName']
    case.case_number = request.GET['NPNum']
    case.case_age = request.GET['NPAge']
    case.case_sex = request.GET['NPGender']
    case.case_height = request.GET['NPHeight']
    case.case_weight = request.GET['NPWeight']
    case.case_history = request.GET['NPCase']
    case.case_blood_type = request.GET['NPBloodType']
    case.case_note = request.GET['NPNote']
    case.save()
    return redirect(all_patient)
