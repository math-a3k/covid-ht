#
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Data


class DataClassificationForm(forms.ModelForm):
    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'unit_ii', 'uuid', 'timestamp', 'is_covid19',
            'chtuid', 'is_finished'
        ]

    def clean(self):
        cleaned_data = super().clean()

        hemogram_fields_count = 0
        threshold = getattr(settings, 'HEMOGRAM_FIELDS_MIN_NUM_SUBMIT', 6)
        fields = self.Meta.model.get_hemogram_main_fields() + \
            self.Meta.model.get_conversion_fields()
        for hfield in fields:
            if cleaned_data.get(hfield, None):
                hemogram_fields_count += 1
        if hemogram_fields_count < threshold:
            raise ValidationError(
                _("At least %(threshold)s hemogram result fields must be "
                  "submitted in order to classify an hemogram."),
                code="not_enough_fields",
                params={'threshold': threshold}
            )
        return cleaned_data


class DataInputForm(forms.ModelForm):
    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'uuid', 'timestamp',
        ]
