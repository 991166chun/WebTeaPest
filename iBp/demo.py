

import sys
import os
import csv
import shutil
from cv2 import cv2
import numpy as np
from .models import Img, Detection, Prediction
from mmcv.image import imread, imwrite
from datetime import datetime


def demo_test():
    img_name = 'test.jpg'
    img = 'media/img/' + img_name

    img = Img(img_name = img_name,
            img_url=img_name,
            date=datetime.now())
    img.save()

    
    demo(str(img_name), img)


def read_label_color(file, BGR=True):
    '''
        Parameters
        ----------
        file : txt file
            format: brownblight 255,102,0 orange
    
        Returns
        -------
        result : dict
            format: [ 'brownblight' : [255, 102, 0]]
    '''
    color_dict = {}
    
    with open(file, 'r') as f:
        lines = f.readlines()
    
    for l in lines:
        strs = l.split(' ')
        label = strs[0]
        color = list(map(int, strs[1].split(',')))
        if BGR:
            color[0], color[2] = color[2], color[0]
        color_dict[label] = color
        
    return color_dict

def rename_time(img_name, img):
    dt = img.date
    date = '{:02d}{:02d}{:02d}{:02d}{:02d}'.format(dt.month, dt.day, dt.hour, dt.minute, dt.second)
    newname = date + '.' + img_name.split('.')[-1]
    o_img = 'media/img/' + img_name 
    n_img = 'media/img/' + newname
    os.rename(o_img, n_img)
    img.img_name = date
    img.img_url = 'img/' + newname
    img.save()
    return n_img, newname

def pred_img(img_name):

    from mmdet.apis import init_detector, inference_detector

    config_file = '/home/chun/TeaDisease/configs/_xm/cascade_webdemo.py'
    # download the checkpoint from model zoo and put it in `checkpoints/`
    checkpoint_file = '/home/chun/TeaDisease/work_dirs/web/crcnn_101x_final.pth'
    # build the model from a config file and a checkpoint file
    model = init_detector(config_file, checkpoint_file, device='cuda:0')
    # test a single image
    

    #img_out = 'media/output/' + img_name
    result = inference_detector(model, img)

    colorfile = 'imgUp/color.txt'
    colors = read_label_color(colorfile)
    
    bbox_result, segm_result = result[:-1], None
    bboxes = np.vstack(bbox_result)
    labels = [
        np.full(bbox.shape[0], i, dtype=np.int32)
        for i, bbox in enumerate(bbox_result)
    ]
    
    labels = np.concatenate(labels)
    return labels, bboxes

def demo(img_name, imgd):

    labels, bboxes = pred_img(img_name)

    colorfile = 'imgUp/color.txt'
    colors = read_label_color(colorfile)

    i = draw_det_bboxes_A(img,
                    bboxes,
                    labels,
                    imgd,
                    colors=colors,
                    width=800,
                    class_names=model.CLASSES,
                    score_thr=0.5,
                    out_file=img)
    return i

def demoIBP(img_name):

    labels, bboxes = pred_img(img_name)

    colorfile = 'imgUp/color.txt'
    colors = read_label_color(colorfile)

    context = draw_bboxes(img_name,
                    bboxes,
                    labels,
                    context,
                    colors=colors,
                    write_det=False,
                    class_names=model.CLASSES,
                    score_thr=0.5,
                    out_file=img_name)
                    
    return context


def draw_det_bboxes_A(img_name,
                        bboxes,
                        labels,
                        imgd,
                        colors,
                        write_det=True,
                        width=None,
                        class_names=None,
                        score_thr=0.5,
                        out_file=None):
    """Draw bboxes and class labels (with scores) on an image.

    Args:
        img (str or ndarray): The image to be displayed.
        bboxes (ndarray): Bounding boxes (with scores), shaped (n, 4) or
            (n, 5).
        labels (ndarray): Labels of bboxes.
        class_names (list[str]): Names of each classes.
        score_thr (float): Minimum score of bboxes to be shown.
        out_file (str or None): The filename to write the image.
    """
    assert write_det & isinstance(imgd, dict):
    assert bboxes.ndim == 2
    assert labels.ndim == 1
    assert bboxes.shape[0] == labels.shape[0]
    assert bboxes.shape[1] == 4 or bboxes.shape[1] == 5
    
    img = imread(img_name)
    img = img.copy()
    
    ori_size = img.shape

    if width == None:
        width = ori_size[0]
        ratio = 1
    else:
        ratio = width/ori_size[0]
        img = cv2.resize(img, (int(ori_size[1]*ratio),int(ori_size[0]*ratio)))
    
    scores = bboxes[:, -1]

    if score_thr > 0.0:
        assert bboxes.shape[1] == 5
        inds = scores > score_thr
        bboxes = bboxes[inds, :]
        labels = labels[inds]
        scores = scores[inds]

    if write_det:
        Pred = Prediction(img_name = str(imgd),
                            pred_num = labels.shape[0],
                            img = imgd)
        Pred.save()

    ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    i = 0
    
    for bbox, label, score in zip(bboxes, labels, scores):
        
        pred_cls = class_names[label]
        color = colors[pred_cls]
        box_id = ABC[i]
        
        bbox = bbox*ratio
        bbox_int = bbox.astype(np.int32)
        if write_det:
            write_det(Pred,
                    box_id,
                    pred_cls,
                    score,
                    bbox_int)
        else:
            write_json()
        
        left_top = (bbox_int[0], bbox_int[1])
        right_bottom = (bbox_int[2], bbox_int[3])
        
        cv2.rectangle(img, (left_top[0], left_top[1]),
                      (right_bottom[0], right_bottom[1]), color, 4)
        text_size, baseline = cv2.getTextSize(box_id,
                                              cv2.FONT_HERSHEY_SIMPLEX, 1.3, 2)
        p1 = (left_top[0], left_top[1] + text_size[1])
        cv2.rectangle(img, tuple(left_top), (p1[0] + text_size[0], p1[1]+1 ), color, -1)
        cv2.putText(img, box_id, (p1[0], p1[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255,255,255), 2, 8)
        
        i += 1
        
        
    print('done   '+ str(out_file))
    
    if out_file is not None:
        imwrite(img, out_file)
    return i


def draw_bboxes(img_name,
                        bboxes,
                        labels,
                        colors,
                        width=800,
                        class_names=None,
                        score_thr=0,
                        out_file=None):
    """Draw bboxes and class labels (with scores) on an image.

    Args:
        img (str or ndarray): The image to be displayed.
        bboxes (ndarray): Bounding boxes (with scores), shaped (n, 4) or
            (n, 5).
        labels (ndarray): Labels of bboxes.
        class_names (list[str]): Names of each classes.
        score_thr (float): Minimum score of bboxes to be shown.
        out_file (str or None): The filename to write the image.
    """
    assert bboxes.ndim == 2
    assert labels.ndim == 1
    assert bboxes.shape[0] == labels.shape[0]
    assert bboxes.shape[1] == 4 or bboxes.shape[1] == 5
    
    img = imread(img_name)
    img = img.copy()
    
    ori_size = img.shape
    ratio = width/ori_size[0]
    img = cv2.resize(img, (int(ori_size[1]*ratio),int(ori_size[0]*ratio)))
    
    scores = bboxes[:, -1]
    if score_thr > 0:
        assert bboxes.shape[1] == 5
        inds = scores > score_thr
        bboxes = bboxes[inds, :]
        labels = labels[inds]
        scores = scores[inds]


    ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    i = 0

    

    for bbox, label, score in zip(bboxes, labels, scores):
        
        pred_cls = class_names[label]
        color = colors[pred_cls]
        box_id = ABC[i]
        
        bbox = bbox*ratio
        bbox_int = bbox.astype(np.int32)
        
        left_top = (bbox_int[0], bbox_int[1])
        right_bottom = (bbox_int[2], bbox_int[3])
        
        cv2.rectangle(img, (left_top[0], left_top[1]),
                      (right_bottom[0], right_bottom[1]), color, 4)
        text_size, baseline = cv2.getTextSize(box_id,
                                              cv2.FONT_HERSHEY_SIMPLEX, 1.3, 2)
        p1 = (left_top[0], left_top[1] + text_size[1])
        cv2.rectangle(img, tuple(left_top), (p1[0] + text_size[0], p1[1]+1 ), color, -1)
        cv2.putText(img, box_id, (p1[0], p1[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255,255,255), 2, 8)
    
    imwrite(img, out_file)                
      
    
    return context

def init_json(dataTime, num):
    context = {
        "dataTime": dataTime, # 時間ID, 與原來接收之ID相同
        # "resultImage": image_file,
        "numofPredictions": 0,           # int, 總計辨識框數量，通常不會多於20
        "pestTable": {   # 共12種病蟲害，每一項目皆為陣列，內含該種類之所有預測結果
            'mosquito_early':[],
            'mosquito_late':[],                                 #'盲椿象_晚期',
            'brownblight': [],                                  #'赤葉枯病',
            'fungi_early': [],   #'真菌性病害_早期',
            'blister': [],                                      #'茶餅病',
            'algal': [],                                        #'藻斑病',
            'miner': [],                                        #'潛葉蠅',
            'thrips': [],        #'薊馬',
            'roller': [],                                       #'茶捲葉蛾_傷口',
            'moth': [],                                         #'茶姬捲葉蛾_傷口',
            'tortrix': [],                                      #'茶姬捲葉蛾_捲葉',
            'flushworm': [],                                    #'黑姬捲葉蛾',
            },
    }

    return context

def write_det(Pred, box_id, pred_cls, score, bbox_int):
    table = {
        'mosquito_early': '盲椿象_早期',
        'mosquito_late':'盲椿象_晚期',
        'brownblight': '赤葉枯病',
        'fungi_early': '真菌性病害_早期',
        'blister': '茶餅病',
        'algal': '藻斑病',
        'miner': '潛葉蠅',
        'thrips':'薊馬',
        'roller': '茶捲葉蛾',
        'mosquito_late': '盲椿象_晚期',
        'mosquito_early': '盲椿象_早期',
        'moth': '茶姬捲葉蛾',
        'tortrix': '茶姬捲葉蛾',
        'flushworm': '黑姬捲葉蛾',
    }

    htable = {
        'mosquito_early': 'mosquito',
        'mosquito_late':'mosquito',
        'brownblight': 'brownblight',
        'fungi_early': 'fungi_early',
        'blister': 'blister',
        'algal': 'algal',
        'miner': 'miner',
        'thrips':'thrips',
        'roller': 'roller',
        'mosquito_late': 'mosquito',
        'mosquito_early': 'mosquito',
        'moth': 'tortrix',
        'tortrix': 'tortrix',
        'flushworm': 'flushworm',
    }

    pred_id = str(Pred).split('.')[0] + '_' + box_id

    context = '{:s}: {:s} score: {:.3f}'.format(box_id, table[pred_cls], score)
    print(context)
    det = Detection(
        pred_id = pred_id,
        img_name = Pred,
        box_id = box_id,
        pred_cls = pred_cls,
        html_file = htable[pred_cls],
        score = score,
        xmin = bbox_int[0],
        ymin = bbox_int[1],
        xmax = bbox_int[2],
        ymax = bbox_int[3],
        context = context,
    )
    det.save()
