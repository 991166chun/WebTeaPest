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
    list_filter = ('finishCheck',)
    def del_selected(modeladmin, request, queryset):
        queryset.delete()
    del_selected.short_description = "Delete selected without check"

    def check_selected(modeladmin, request, queryset):
        
        for fb in queryset:
            fb.finishCheck = True
            fb.save()
            
    check_selected.short_description = '將選取項目設為已完成'

    list_display = ('feedbackID', 'feedback', 'review', 'date', 'finishCheck')
    actions = [del_selected, check_selected]

    def link_to_user(self, obj):
        link = reverse("admin:imgUp_Img_change", args=[obj.user_id])
        return format_html('<a href="{}">Edit {}</a>', link, obj.Img.img_name)
    link_to_user.short_description = 'Edit user'

admin.site.register(Feedback, FeedbackAdmin)

