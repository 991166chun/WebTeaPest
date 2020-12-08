from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from .models import Img, Detection, Feedback
from .forms import Feedbacks
from .demo import demo
from datetime import datetime
#from django.utils import timezone
#import pytz
import os
import shutil
import json

# Create your views here.

default_context = {
    'error_message' : '',
    'imgs': 'img_model',
    'dets': 'dets query set',
    'dets2': 'dets query set',
}


def main(request):

    return render(request, 'index.html')
            
def id2result(imgid):
    try: 
        url = reverse('show_image', kwargs={'img_id': imgid} )
        return redirect('{}#result'.format(url))
    except:
        err = 'id_not_found'
        url = reverse('error', kwargs={'issue': err} )
        return redirect('{}#upload'.format(url))

def uploadImg(request):

    if request.method == 'POST':
        # if True:
        try:
            img_name = request.FILES.get('img')
            datatime = datetime.now()
            img_name, img = rename_time(img_name, datatime)

            num = demo(img_name, img)

            return id2result(img.img_name)
        except:
            err = 'wrong_input'
            url = reverse('error', kwargs={'issue': err} )
            return redirect('{}#upload'.format(url))

    return render(request, 'imgUpload.html')


def rename_time(img_mem, datatime):
    dt = datatime

    img = Img(img_name = img_mem,
                img_url=img_mem,
                date=dt)
    img.save()
    
    img_name = str(img_mem)
    date = '{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}'.format(dt.year-2000,
                                                             dt.month, dt.day,
                                                             dt.hour, dt.minute, 
                                                             dt.second, dt.microsecond % 100)
    newname = date + '.' + img_name.split('.')[-1]

    o_img = 'media/img/' + img_name 
    n_img = 'media/img/' + newname
    os.rename(o_img, n_img)

    copimg = 'media/ori_image/' + newname
    shutil.copyfile(n_img, copimg)

    img.img_name = date
    img.img_url = 'img/' + newname

    img.save()

    return n_img, img

def showHistory(request):
    try:
        imgid = request.POST['imgid']

        return id2result(imgid)
    except:
        err = 'id_not_found'
        url = reverse('error', kwargs={'issue': err} )
        return redirect('{}#upload'.format(url))

def errorpage(request, issue):
    
    errors = {
        'id_not_found': 'ERROR: 輸入ID錯誤，該影像不存在',
        'wrong_input': 'ERROR: 未選擇檔案or檔名須為英文',
        'not_yet': 'ERROR: 未有影像上傳，請先上傳影像',
    }
    img = Img.objects.get(img_name='noimg')
    context = {
        'error_message' : errors[issue],
        'imgs': img,
    }
    return render(request, 'index.html', context)
    

def showHtml(request, f):
    context = {}
    values = request.path
    print(f)
    return render(request, values[1:], context)

def showImg(request, img_id=None):
    
    if img_id == None:
        img = Img.objects.latest()

    else:
        try:
            img = Img.objects.get(img_name=img_id)
        except:
            err = 'id_not_found'
            url = reverse('error', kwargs={'issue': err} )
            return redirect('{}#upload'.format(url))

    dets = Detection.objects.filter(img_data=img)
    context = {
        'imgs': img,
        'dets': dets,
        'dets2': dets,
    }
    return render(request, 'index.html', context)

def feedback(request):

    if request.POST['feedback'] is not '':

        pred_id = request.POST['pred_id']
        det = Detection.objects.get(pred_id=pred_id)
        fb = Feedback(
            pred = det,
            date = datetime.now(),
            issue= request.POST['issue'],
            feedback = request.POST['feedback'],
        )
        fb.save()

    img_id = request.POST['img_id']
    return id2result(img_id)

def add_region(request):
    if True:
    # try:
        imgid = request.POST['imgid']
        img = Img.objects.get(img_name=imgid)

        region = request.POST['region']
        altitude = request.POST['altitude']

        img.region = region
        img.altitude = altitude

        img.save()
        return id2result(imgid)
    # except:
    #     err = 'not_yet'
    #     url = reverse('error', kwargs={'issue': err} )
    #     return redirect('{}#upload'.format(url))

    
def db_test(img, result):

    det = Detection(
        pred_id = '0001_A',
        # img_name = Pred,
        img_data = img,
        box_id = 'A',
        pred_cls = 'brownblight' ,
        score = 0.995,
        xmin = 100,
        ymin = 100,
        xmax = 200,
        ymax = 200,
        context = 'A: brownblight score: 0.995',
    )
    det.save()


def det_to_json(img_name, result, classes):
    json_name = img_name[:-4] + '.json'
    det_count = 0
    det_dict = {}
    for i in range(len(result)):
        pred_cls = classes[i]
        if len(result[i]) == 0:
            det_dict[pred_cls] = []
        else:
            pass
    
