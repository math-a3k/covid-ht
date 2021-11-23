#
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Data


class GroupedFieldsFormMixin:

    def get_grouped_fields(self):
        grouped_fields = []
        processed_fields = []
        for field in self.fields:
            if field not in processed_fields:
                conversion_fields = [
                    f.attname for f in self._meta.model._meta.get_fields()
                    if f.attname.startswith(field + "_U")
                ]
                if not conversion_fields:
                    grouped_fields.append([field])
                    processed_fields.append(field)
                else:
                    group = [field, ]
                    for c_field in conversion_fields:
                        group.append(c_field)
                    grouped_fields.append(group)
                    processed_fields.extend(group)
        return grouped_fields


def get_classification_fields():
    if settings.DATA_CLASSIFICATION_FORM_FIELDS == '__all__':
        fields = Data.AUXILIARY_FIELDS + \
            Data.get_main_fields() + \
            Data.get_conversion_fields()
        return fields
    else:
        return settings.DATA_CLASSIFICATION_FORM_FIELDS


class DataClassificationForm(GroupedFieldsFormMixin, forms.ModelForm):
    class Meta:
        model = Data
        fields = get_classification_fields()

    def clean(self):
        cleaned_data = super().clean()

        clinical_fields_count = 0
        threshold = getattr(settings, 'CLINICAL_FIELDS_MIN_NUM_SUBMIT', 6)
        clinical_fields = self.Meta.model.get_main_fields() + \
            self.Meta.model.get_conversion_fields()
        for field in clinical_fields:
            if cleaned_data.get(field, None):
                clinical_fields_count += 1
        if clinical_fields_count < threshold:
            raise ValidationError(
                _("At least %(threshold)s clinical fields must be "
                  "submitted in order to classify a clinical result."),
                code="not_enough_fields",
                params={'threshold': threshold}
            )
        return cleaned_data


class DataInputForm(GroupedFieldsFormMixin, forms.ModelForm):
    class Meta:
        model = Data
        fields = \
            ['unit_ii', Data.LEARNING_LABELS, ] + \
            settings.DATA_INPUT_FORM_FIELDS + \
            ['is_finished', ]
