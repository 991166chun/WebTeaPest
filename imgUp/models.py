from django.db import models
from datetime import datetime

# Create your models here.
class Img(models.Model):

    img_name = models.CharField(max_length=100, default='unknow', help_text='image name of the prediction')
    img_url = models.ImageField(upload_to='img')
    #out_url = models.ImageField(upload_to='output')
    date = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['-date']
        get_latest_by = "date"

    def __str__(self):
        return str(self.img_name)

class Prediction(models.Model):
    '''
    img_name = '0001.jpg'
    pred_num = 5
    img = img
    '''
    img_name = models.CharField(max_length=100, help_text='image name of the prediction')
    pred_num = models.IntegerField()
    img = models.OneToOneField(Img, on_delete=models.CASCADE)

    class Meta:
        ordering = ['img']

    def __str__(self):
        return self.img_name

class Detection(models.Model):
    '''
    store three highest pred result
    pred_id = '0001_A'
    img_name = '0001.jpg'
    box_id = 'A'
    pred_cls = 'brownblight' 
    score = 0.995
    pred_box = [100,100,200,200]
    context = 'A: brownblight score: 0.995'
    '''
    
    pred_id = models.CharField(max_length=100, primary_key=True)
    img_name = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    box_id = models.CharField(max_length=1, help_text='ABCDE')
    pred_cls = models.CharField(max_length=20)
    html_file = models.CharField(max_length=20, null=True)
    score = models.FloatField()
    xmin = models.IntegerField()
    ymin = models.IntegerField()
    xmax = models.IntegerField()
    ymax = models.IntegerField()
    context = models.TextField(max_length=100, help_text='A: 赤葉枯病 score: 0.995')

    class Meta:
        ordering = ['img_name', 'box_id']
    
    def __str__(self):
        return str(self.img_name) + ' ' + self.context





