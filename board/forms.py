from django import forms
from .models import Ad, Response
from ckeditor_uploader.fields import RichTextUploadingField




class AdForm(forms.ModelForm):

   class Meta:
       model = Ad
       fields = ['category',
                 'title',
                 'content',
                 ]

       widgets = {
           'content': RichTextUploadingField(config_name='extends'),
       }

       labels = {
           'category': '',
           'title': '',
           'content': '',
       }


       error_messages = {
           'title': {
                'max_length' : 'Максимальная длина не может быть больше 250 символов '
            },
        }


class ResponsesForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['content']