from django.contrib import admin

# Register your models here.
from .models import Img, Detection, Prediction, Feedback
# from .forms import Feedbacks

admin.site.register(Img)
admin.site.register(Detection)
admin.site.register(Prediction)
# admin.site.register(Feedback)
# admin.site.register(Feedbacks)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('pred', 'feedback', 'date')

admin.site.register(Feedback, FeedbackAdmin)