from django.contrib import admin

# Register your models here.
from .models import Img, Detection, Prediction, Feedback
# from .forms import Feedbacks

class ImgAdmin(admin.ModelAdmin):
    # list_display = ('img_name','date'）
    list_display = ('img_name','date','image_preview')
    readonly_fields = ('image_preview',)

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview

    thumbnail_preview.short_description = 'Thumbnail Preview'
    thumbnail_preview.allow_tags = True

admin.site.register(Img, ImgAdmin)


admin.site.register(Detection)
admin.site.register(Prediction)
# admin.site.register(Feedback)
# admin.site.register(Feedbacks)

class FeedbackAdmin(admin.ModelAdmin):

    def del_selected(modeladmin, request, queryset):
        queryset.delete()
    del_selected.short_description = "Delete selected without check"

    list_display = ('pred', 'feedback', 'date')
    actions = [del_selected,]

admin.site.register(Feedback, FeedbackAdmin)

