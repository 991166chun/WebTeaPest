

import sys
import os
import csv
import shutil
from cv2 import cv2
import numpy as np
from .models import Img, Detection
from mmcv.image import imread, imwrite
import pytz
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

def pred_img(img_name):

    # print('import library')

    from mmdet.apis import init_detector, inference_detector

    # print('load model')
    config_file = '/home/chun/TeaDisease/configs/_xm/cascade_webdemo.py'
    # download the checkpoint from model zoo and put it in `checkpoints/`
    checkpoint_file = '/home/chun/TeaDisease/work_dirs/web/crcnn_101x_final.pth'
    # build the model from a config file and a checkpoint file
    model = init_detector(config_file, checkpoint_file, device='cuda:0')
    # test a single image
    # print('test a single image')
    #img_out = 'media/output/' + img_name
    result = inference_detector(model, img_name)
    
    bbox_result, _ = result[:-1], None
    bboxes = np.vstack(bbox_result)
    labels = [
        np.full(bbox.shape[0], i, dtype=np.int32)
        for i, bbox in enumerate(bbox_result)
    ]
    
    labels = np.concatenate(labels)
    classes = model.CLASSES
    return labels, bboxes, classes

def demo(img_name, imgd):

    labels, bboxes, classes = pred_img(img_name)
    # print('drawing box')

    colorfile = '/home/chun/teadiagnose/imgUp/color.txt'
    colors = read_label_color(colorfile)

    i = draw_det_bboxes_A(img_name,
                        bboxes,
                        labels,
                        imgd,
                        colors=colors,
                        width=800,
                        class_names=classes,
                        score_thr=0.5,
                        out_file=img_name)
    return i



def draw_det_bboxes_A(img_name,
                        bboxes,
                        labels,
                        imgd,
                        colors,
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

    if score_thr > 0.0:
        assert bboxes.shape[1] == 5
        inds = scores > score_thr
        bboxes = bboxes[inds, :]
        labels = labels[inds]
        scores = scores[inds]

    # Pred = Prediction(img_name = str(imgd),
    #                     pred_num = labels.shape[0],
    #                     img = imgd)
    # Pred.save()

    imgd.pred_num = labels.shape[0]
    imgd.save()

    if labels.shape[0]==0 :
        write_det(imgd,
                box_id='',
                pred_cls='',
                score=0,
                bbox_int=None,
                nodet=True)

    ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    i = 0
    
    for bbox, label, score in zip(bboxes, labels, scores):
        
        pred_cls = class_names[label]
        color = colors[pred_cls]
        box_id = ABC[i]
        
        bbox = bbox*ratio
        bbox_int = bbox.astype(np.int32)

        write_det(imgd,
                box_id,
                pred_cls,
                score,
                bbox_int)
        
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



def write_det(Img, box_id, pred_cls, score, bbox_int, nodet=False):
    if nodet:
        pred_id = str(Img) + '_N'
        det = Detection(
            pred_id = pred_id,
            img_name = os.path.basename(Img.img_url.url),
            img_data = Img,
            box_id = box_id,
            pred_cls = 'NaN',
            html_file = 'blank',
            score = score,
            xmin = 0,
            ymin = 0,
            xmax = 0,
            ymax = 0,
            context = '未偵測到病蟲害',
        )
        det.save()
    else:
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

        pred_id = str(Img) + '_' + box_id

        context = '{:s}: {:s} score: {:.3f}'.format(box_id, table[pred_cls], score)
        print(context)
        det = Detection(
            pred_id = pred_id,
            img_name = os.path.basename(Img.img_url.url),
            img_data = Img,
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
