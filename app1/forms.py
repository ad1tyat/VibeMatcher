from django import forms

from django.core import validators


class HomeForm(forms.Form):
    track_name = forms.CharField(max_length=256)

