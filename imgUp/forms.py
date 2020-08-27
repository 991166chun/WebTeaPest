from django import forms
from .models import Detection
from datetime import datetime

class Feedbacks(forms.Form):
    det = forms.ModelChoiceField(queryset=Detection.objects.all(), label='pred_id')
    dtime = forms.DateTimeField(label='time', initial=datetime.now)
    feedback = forms.CharField(label='feedback', widget=forms.Textarea)