from imgUp.models import Img, Detection, Feedback
from django.utils import timezone
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from wutils.mail import sendSimpleEmail, mailform, sendAttachEmail
import pytz
import csv

htable = {
    'brownblight': '赤葉枯病',
    'fungi_early': '真菌性病害',
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

columns = ['起始日', '結算日', '影像張數',
            '赤葉枯病', '茶餅病', '藻斑病', '真菌性病害',
            '潛葉蠅', '薊馬', '盲椿象_早期', '盲椿象_晚期',
            '茶捲葉蛾', '茶姬捲葉蛾', '黑姬捲葉蛾', '備註']

class Collector():

    def __init__(self, settle_date=timezone.now(), period=7):

        settle = settle_date
        end = settle_date + timedelta(days=1)
        begin = end - timedelta(days=period)

        self.settle = str(settle.date())
        self.begin = str(begin.date())
        self.end = str(end.date())

        self.disease_num = 11


    def upload_count(self):

        begin = self.begin
        end = self.end
        print('search date from %s to %s' %(begin, end))
        imgs = Img.objects.filter(date__range=[begin, end])
        self.uploaded = imgs.count()
        
        return imgs.count()

    def disease_count(self, remark=''):
        '''
        get img
            get det
                det++
        format 
        '''
        report_data = [0] * len(columns)

        begin = self.begin
        end = self.end
        sett = self.settle

        report_data[0] = begin
        report_data[1] = sett

        imgs = Img.objects.filter(date__range=[begin, end])
        report_data[2] = imgs.count()

        for img in imgs:
            dets = Detection.objects.filter(img_data=img)
            
            for det in dets:
                clsname = det.pred_cls
                cid = columns.index(htable[clsname])
                report_data[cid] += 1
        
        report_data[-1] = remark

        return report_data
            


    def write_csv(self, csvfile, remark=''):
        
        report_data = self.disease_count(remark)
        
        with open(csvfile, 'a', newline='',encoding='utf-8-sig') as csvf:

            writer = csv.writer(csvf)
            writer.writerow(report_data)
        
        self.report_data = report_data
    
    def init_csv(self, csvfile):

        with open(csvfile, 'w', newline='', encoding='utf-8-sig') as csvf:

            writer = csv.writer(csvf)

            example = ['2000-01-01', '2000-01-07', '20',
                         '1', '2', '3', '4', '5',
                         '6', '7', '8', '9', '10', '11', '測試資料']

            writer.writerow(columns)
            writer.writerow(example)

        print('created new report file: ',csvfile)

    def gen_text(self):

        report_data = self.report_data

        text = ['每周統計回報:',]
        text.append('\t統計時間週期: %s - %s' % (report_data[0], report_data[1]))
        text.append('\t上傳影像張數: %d' % (report_data[2]))
        text.append('\t病蟲害統計: ')
        for i in range(3, len(report_data)-1):
            text.append('\t\t%s: %d' % (columns[i], report_data[i]))
        
        if report_data[-1] == '':
            report_data[-1] = '無'
        
        text.append('\t備註: %s' % (report_data[-1]))

        txtfile = 'wutils/report-%s.txt' % report_data[1]

        with open(txtfile, 'w') as f:
            for t in text:
                f.write(t)
                f.write('\n')

        return txtfile

    def gen_figure(self, report_data, fig_name='2020-01-01-report.png'):

        
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        fig = plt.figure()
        x = 10
        s = self.gen_text(report_data)
        # for i in range(12):
        #     y = 10 + i*10 
        #     plt.text(x, y, s[i])
        # fig.savefig(fig_name)
        # with open()


# print(__name__)
if __name__ == "__main__":
    coller = Collector()
    print('Images uploaded this week: ',coller.upload_count())
    csv_test = 'wutils/test.csv'
    # coller.init_csv(csv_test)
    coller.write_csv(csv_test)
    subject = '病蟲害辨識系統每周回報'
    user = '研究員'
    week = '01/01-01/07'
    text = mailform(user, week, coller.begin, coller.settle)
    attach = coller.gen_text()
    mailTo = ['r07631006@ntu.edu.tw',]
    sendAttachEmail(subject, text, mailTo, attach)