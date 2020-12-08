from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import TextInput, Textarea
# Register your models here.
from .models import Img, Detection, Feedback
# from .forms import Feedbacks

class ImgAdmin(admin.ModelAdmin):
    list_display = ('img_name','date','image_preview')
    readonly_fields = ('image_preview',)

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview

    thumbnail_preview.short_description = 'Thumbnail Preview'
    thumbnail_preview.allow_tags = True



admin.site.register(Img, ImgAdmin)


class DetAdmin(admin.ModelAdmin):
    list_display = ('pred_id','link_to_Img')
    
    def link_to_Img(self, obj):
        url = reverse("admin:imgUp_img_change", args=[obj.img_data.id]) #model name has to be lowercase
        link = '<a href="%s">%s</a>' % (url, obj.img_data.img_name)
        return mark_safe(link)
    link_to_Img.allow_tags=True
    link_to_Img.short_description = 'Image'




admin.site.register(Detection, DetAdmin)
# admin.site.register(Prediction)
# admin.site.register(Feedback)
# admin.site.register(Feedbacks)

class FeedbackAdmin(admin.ModelAdmin):

    def del_selected(modeladmin, request, queryset):
        queryset.delete()
    del_selected.short_description = "Delete selected without check"

    list_display = ('pred', 'feedback', 'date')
    readonly_fields = ('image_preview',)
    actions = [del_selected,]

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview

    thumbnail_preview.short_description = 'Thumbnail Preview'
    thumbnail_preview.allow_tags = True
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }

admin.site.register(Feedback, FeedbackAdmin)

