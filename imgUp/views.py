from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from .models import Img, Detection, Prediction, Feedback
from .forms import Feedbacks
from .demo import demo
from datetime import datetime
#from django.utils import timezone
#import pytz
import os
import shutil
import json

# Create your views here.

def main(request):

    if request.method == 'POST':
        print(request.FILES)
        if 'img' in request.FILES:
            return uploadImg(request)

        elif 'feedback' in request.POST:
            return feedback(request)

        else:
            context = {
                'error_message' : 'ERROR: 未選擇檔案or檔名須為英文'
            }

            return render(request, 'wrongInput.html', context)
            
    
    return render(request, 'imgUpload.html')

def uploadImg(request):

    if request.method == 'POST':
        if True:
        # try:
            img_name = request.FILES.get('img')
            datatime = datetime.now()
            img_name, img = rename_time(img_name, datatime)

            num = demo(img_name, img)

            pred = Prediction.objects.get(img=img)
            dets = Detection.objects.filter(img_name=pred)
            print(img.img_url)
            print(img.img_url.url)
            
            context = {
                'imgs': img,
                'dets': dets,
                'dets2': dets,
            }

            if num == 0:
                return render(request, 'NoResult.html', context)

            return render(request, 'showImg2.html', context)
        # except:
        #     # if file empty or invalid file name
        #     context = {
        #         'error_message' : 'ERROR: 未選擇檔案or檔名須為英文'
        #     }

        #     return render(request, 'wrongInput.html', context)

    return render(request, 'imgUpload.html')


def rename_time(img_mem, datatime):
    dt = datatime

    img = Img(img_name = img_mem,
                img_url=img_mem,
                date=dt)
    img.save()
    img_name = str(img_mem)
    date = '{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}'.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    newname = date + '.' + img_name.split('.')[-1]

    o_img = 'media/img/' + img_name 
    n_img = 'media/img/' + newname
    os.rename(o_img, n_img)

    copimg = 'media/ori_image/' + img_name
    shutil.copyfile(n_img, copimg)

    img.img_name = date
    img.img_url = 'img/' + newname

    img.save()

    return n_img, img



def showHistory(request):

    imgid = request.GET['imgid']
    
    try:
        img = Img.objects.get(img_name=imgid)
        pred = Prediction.objects.get(img=img)
        dets = Detection.objects.filter(img_name=pred)
        context = {
            'imgs': img,
            'dets': dets,
            'dets2': dets,
        }

        return render(request, 'showImg2.html', context)

    except:

        context = {
                'error_message' : 'ERROR: 輸入ID錯誤，該影像不存在'
            }
        return render(request, 'wrongInput.html', context)
        # return redirect('uploadImg')



def showHtml(request, f):
    context = {}
    values = request.path
    print(f)
    return render(request, values[1:], context)

def showImg(request, img_id=None):
    
    if img_id == None:
        img = Img.objects.latest()
    else:
        img = Img.objects.get(img_name=img_id)
    pred = Prediction.objects.get(img=img)
    dets = Detection.objects.filter(img_name=pred)
    context = {
        'imgs': img,
        'dets': dets,
        'dets2': dets,
    }
    return render(request, 'showImg2.html', context)

def getStart(request):
    context = {}
    return render(request, 'base.html', context)

def showDemo(request):
    context = {}
    return render(request, 'demo.html', context)



def feedback(request):

    if request.POST['feedback'] is not '':

        # form = Feedbacks(request.POST)
        # print('form is valid :', form.is_valid())
        pred_id = request.POST['pred_id']
        det = Detection.objects.get(pred_id=pred_id)
        fb = Feedback(
            pred = det,
            date = datetime.now(),
            feedback = request.POST['feedback'],
        )
        fb.save()

    img_id = request.POST['img_id']

    # img_name = request.FILES.get('img')
    return showImg(request, img_id)


    
def db_test(img, result):

    Pred = Prediction(
        img_name = '0001.jpg',
        pred_num = 5,
        img = img,
    )
    Pred.save()

    det = Detection(
        pred_id = '0001_A',
        img_name = Pred,
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
    
