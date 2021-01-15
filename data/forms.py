#
from django import forms

from .models import Data


class DataClassificationForm(forms.ModelForm):
    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'unit_ii', 'uuid', 'timestamp', 'is_covid19'
        ]


class DataInputForm(forms.ModelForm):
    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'uuid', 'timestamp',
        ]
