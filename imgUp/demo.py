

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

    
    demo2(str(img_name), img)


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
    img.img_name = newname
    img.img_url = 'img/' + newname
    img.save()
    return n_img , newname

def demo2(img_name, imgd):
    from .mmdetection.mmdet.apis import init_detector, inference_detector

    config_file = 'imgUp/mmdetection/cascade.py'
    # download the checkpoint from model zoo and put it in `checkpoints/`
    checkpoint_file = 'imgUp/mmdetection/epo_72_cas_50.pth'
    # build the model from a config file and a checkpoint file
    model = init_detector(config_file, checkpoint_file, device='cuda:0')
    # test a single image
    o_img = img_name
    img, img_name = rename_time(o_img, imgd)
    
    copimg = 'media/ori_image/' + img_name
    shutil.copyfile(img, copimg)

    #img_out = 'media/output/' + img_name
    result = inference_detector(model, img)

    colorfile = 'imgUp/color.txt'
    colors = read_label_color(colorfile)
    
    bbox_result, segm_result = result, None
    bboxes = np.vstack(bbox_result)
    labels = [
        np.full(bbox.shape[0], i, dtype=np.int32)
        for i, bbox in enumerate(bbox_result)
    ]
    labels = np.concatenate(labels)
    
    draw_det_bboxes_A(img,
                    bboxes,
                    labels,
                    imgd,
                    colors=colors,
                    width=800,
                    class_names=model.CLASSES,
                    score_thr=0.3,
                    out_file=img)



def draw_det_bboxes_A(img_name,
                        bboxes,
                        labels,
                        imgd,
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
        
        write_det(Pred,
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
        'roll_leaf': '茶捲葉蛾',
        'mosquito': '盲椿象',
        'mos_dot': '盲椿象_晚期',
        'mos_early': '盲椿象_早期',
        'mos_larva': '盲椿象_早期',
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
        'roll_leaf': 'roller',
        'mosquito': 'mosquito',
        'mos_dot': 'mosquito',
        'mos_early': 'mosquito',
        'mos_larva': 'mosquito',
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

'''
--------------------------------------------------------------------------------------------------
'''
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
    # show_result_pyplot(img, result, model.CLASSES)
    show_result(img,
                result,
                model.CLASSES,
                score_thr=0.3,
                show=False,
                out_file=img_out)