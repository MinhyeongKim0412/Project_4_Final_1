#윤창현
from django import forms

class MissionImageForm(forms.Form):
    before_image = forms.ImageField(label='이전 사진')
    after_image = forms.ImageField(label='이후 사진')