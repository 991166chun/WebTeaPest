from django.shortcuts import render, redirect
import requests
from ..demo import demoIBP
# Create your views here.



def main(request):

    if request.method == 'POST':
        print(request.FILES)
        if 'img' in request.FILES:
            return process(request)

        else:
            pass

def process(request):

    if request.method == 'POST':
        # if True:
        try:
            img_name = request.FILES.get('img')

            print(img_name)
            
            context = demoIBP(str(img_name))


            return requests.post('', data = context)
            
        except:

            pass
            # if file empty or invalid file name
            # context = {
            #     'error_message' : 'ERROR: 未選擇檔案or檔名須為英文'
            # }

            # return render(request, 'wrongInput.html', context)

    # return render(request, 'imgUpload.html')
