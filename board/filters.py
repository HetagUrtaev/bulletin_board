from urllib import request
import django_filters
from .models import Response, Ad, User, RESPONSE_STATUSES, Category
from django import forms

class TruncatedSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if len(str(label)) > 40:
            option['label'] = str(label)[:40] + '...'
        return option

class ResponseFilter(django_filters.FilterSet):
    ad = django_filters.ModelChoiceFilter(
        field_name='ad',
        to_field_name='id',
        label='Объявление',
        empty_label='Все объявления',
        widget=TruncatedSelect
    )

    def __init__(self, data=None, queryset=None, request=None, **kwargs):
        super().__init__(data, queryset, **kwargs)
        if request and request.user.is_authenticated:
            self.filters['ad'].queryset = Ad.objects.filter(
                author=request.user
            ).order_by('-created_at')
        else:
            self.filters['ad'].queryset = Ad.objects.none()

    class Meta:
        model = Response
        fields = ['ad']