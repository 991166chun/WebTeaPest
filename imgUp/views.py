import os
import shutil
import json
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect, HttpResponse
from .models import Img, Detection, Feedback
from TeaData.models import County, City
from .demo import demo
from .exifGps import get_gps
from datetime import datetime
from numpy.random import randint
from django.utils import timezone
import pytz

# Create your views here.

default_context = {
    'counties' : County.objects.all(),
    'cities' : City.objects.none(),
    'imgs' : Img.objects.get(img_id='noimg')
}


issue_d = {
    '1':'wrong',
    '2':'background',
    '3':'nodetect',
    '4':'other'
    }


def main(request):
    context = {}
    return render(request, 'index.html', {**default_context, **context})
            
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
            img_name, img = save_image(img_name)

            num = demo(img_name, img)
            if request.POST.get('nope', False):
                pass
            else:
                save_region(request, img)

            return id2result(img.img_id)
        except:

            err = 'wrong_input'
            url = reverse('error', kwargs={'issue': err} )
            return redirect('{}#upload'.format(url))

    return render(request, 'imgUpload.html')


def save_image(img_mem):
    
    img = Img(img_url=img_mem)
    img.save()

    ms_id = str(img.img_url).split('-')[-1].split('.')[0]
    nn = "%02d" % randint(0,99)
    imgid = nn + ms_id
    print('img_id: ', imgid)
    img.img_id = imgid
    img.save()

    url = img.img_url.url

    basename = os.path.basename(url)
    imgname = 'media/img/' + basename 
    copimg = 'media/ori_image/' + basename
    shutil.copyfile(imgname, copimg)

    gps = get_gps(imgname)
    print('gps: ', gps)
    if gps is not None:
        img.gps = str(gps)
        img.save()

    return imgname, img

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
        'id_not_found': 'ERROR: 輸入ID錯誤，該影像不存在 The Image ID not exist! ',
        'wrong_input': 'ERROR: 未選擇檔案or檔名須為英文 The uploaded file must be Image!',
        'not_yet': 'ERROR: 未有影像上傳，請先上傳影像 Please upload image first.',
    }
    img = Img.objects.get(img_id='noimg')
    context = {
        'error_message' : errors[issue],
        'imgs': img,
    }
    return render(request, 'index.html', {**default_context, **context})
    

def showHtml(request, f):
    context = {}
    values = request.path
    print(f)
    return render(request, values[1:], {**default_context, **context})

def showImg(request, img_id=None):
    
    print(img_id)
    try:
        img = Img.objects.get(img_id=img_id)
    except:
        err = 'id_not_found'
        url = reverse('error', kwargs={'issue': err} )
        return redirect('{}#upload'.format(url))
    
   
    dets = Detection.objects.filter(img_data=img)

    context = {
        'imgs': img,
        'dets': dets,
    }
    return render(request, 'index.html', {**default_context, **context})

def feedback(request):

    if request.POST['feedback'] != '':

        pred_id = request.POST['pred_id']
        issue_num = request.POST['issue'][0]
        email = request.POST['contact']

        det = Detection.objects.get(pred_id=pred_id)
        fb = Feedback(
            pred = det, 
            date = datetime.now(),
            issue= issue_d[issue_num],
            contact=email,
            feedback = request.POST['feedback'],
        )
        fb.save()

    img_id = request.POST['img_id']
    return id2result(img_id)

def load_cities(request):
    
    # print('load city~~!!')
    if request.method == 'GET' and request.is_ajax():
        county = request.GET.get('county')
        selectCounty = County.objects.get(name=county)
        cities = City.objects.filter(County=selectCounty)
        # print("cities are: ", cities)
        result_set = []
        for city in cities:
            # print("city name", city.name)
            result_set.append({'name': city.name})
        return HttpResponse(json.dumps(result_set), content_type='application/json')
    

def save_region(request, img):

    if True:
    # try:
        county = request.POST['county']
        city = request.POST['city']
        altitude = request.POST['altitude']
        if county != "":
            img.county = County.objects.get(name=county)
        if city != "":
            if city[0] != "-":
                img.city = City.objects.get(name=city, County=img.county)
        if altitude[0] != "-":
            img.altitude = altitude

        img.save()

def add_region(request):
    # if True:
    try:
        imgid = request.POST['imgid']
        print('set region imgid:' , imgid)
        img = Img.objects.get(img_id=imgid)

        county = request.POST['county']
        city = request.POST['city']
        altitude = request.POST['altitude']

        img.county = County.objects.get(name=county)
        img.city = City.objects.get(name=city, County=img.county)
        img.altitude = altitude

        img.save()
        return id2result(imgid)
    except:
        err = 'not_yet'
        url = reverse('error', kwargs={'issue': err} )
        return redirect('{}#upload'.format(url))

    
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
    
def mail_test(request):

    pass


