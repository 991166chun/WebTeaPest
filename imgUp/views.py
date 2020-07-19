from django.shortcuts import render
from .models import Img, Detection, Prediction
from .demo import demo2
from datetime import datetime
#from django.utils import timezone
#import pytz
import json

# Create your views here.
def uploadImg(request):
    if request.method == 'POST':
        img_name = request.FILES.get('img')
        print(img_name)

        img = Img(img_name = img_name,
                  img_url=img_name,
                  date=datetime.now())
        print(img.img_url.url)
        img.save()

        demo2(str(img_name), img)

        pred = Prediction.objects.get(img=img)
        dets = Detection.objects.filter(img_name=pred)
        context = {
            'imgs': img,
            'dets': dets,
            'dets2': dets,
        }
        return render(request, 'showImg2.html', context)

    return render(request, 'imgUpload.html')

def showHtml(request, f):
    context = {}
    values = request.path
    print(f)
    return render(request, values[1:], context)

def showImg(request):
    
    img = Img.objects.latest()
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






def demo(img_name):
    from .mmdetection.mmdet.apis import init_detector, inference_detector, show_result
    import mmcv
    config_file = 'imgUp/mmdetection/cascade.py'
    # download the checkpoint from model zoo and put it in `checkpoints/`
    checkpoint_file = 'imgUp/mmdetection/epo_72_cas_50.pth'
    # build the model from a config file and a checkpoint file
    model = init_detector(config_file, checkpoint_file, device='cuda:0')
    # test a single image
    img = 'media/img/' + img_name
    img_out = 'media/output/' + img_name
    result = inference_detector(model, img)
    # show the results
    # 'brownblight', 'fungi_early', 'blister', 'algal', 'miner', 
    # 'thrips', 'roller', 'roll_leaf', 'mosquito', flushworm'
    # show_result_pyplot(img, result, model.CLASSES)
    print(model.CLASSES)
    show_result(img,
                result,
                model.CLASSES,
                score_thr=0.3,
                show=False,
                out_file=img)
    return result


    
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
    
