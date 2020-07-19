from django.contrib import admin

# Register your models here.
from .models import Img, Detection, Prediction

admin.site.register(Img)
admin.site.register(Detection)
admin.site.register(Prediction)