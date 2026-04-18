from django import forms
from .models import Ad, Response, Category
from ckeditor_uploader.fields import RichTextUploadingField




class AdForm(forms.ModelForm):
   category = forms.ModelChoiceField(
       queryset=Category.objects.all(),
       empty_label='Выберите категорию',
       label = ''
   )

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
        widgets = {'content' : forms.Textarea(attrs={'cols':80, 'rows':4, 'class':'w-100'})}
        labels = {'content' : ''}