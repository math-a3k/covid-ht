#
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinValueValidator, )
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Data


class DataAugmentedForm(forms.ModelForm):
    PERCENTAGE_FIELDS = ['p_neut', 'p_lymp', 'p_mono', 'p_eo', 'p_baso']

    p_neut = forms.DecimalField(
        label=_("NEUT (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Neutrophils (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.9)]
    )
    p_lymp = forms.DecimalField(
        label=_("LYMPH (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Lymphocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.9)]
    )
    p_mono = forms.DecimalField(
        label=_("MONO (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Monocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.9)]
    )
    p_eo = forms.DecimalField(
        label=_("EO (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Eosinophils (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.9)]
    )
    p_baso = forms.DecimalField(
        label=_("BASO (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Basophils (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.9)]
    )

    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'uuid', 'timestamp',
        ]

    def clean(self):
        cleaned_data = super().clean()
        # import ipdb; ipdb.set_trace()
        for field in self.PERCENTAGE_FIELDS:
            if cleaned_data[field] and not cleaned_data.get('wbc', None):
                self.add_error('wbc', ValidationError(
                    _("WBC must be present in order to use percentage "
                      "fields."),
                    code="wbc_not_present",
                ))
                break
        # Convert to absolute values in the correspondent field
        if cleaned_data.get('wbc', None):
            if cleaned_data['p_neut']:
                cleaned_data['neut'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_neut'] / 100)\
                    .quantize(Decimal('10.00'))
            if cleaned_data['p_lymp']:
                cleaned_data['lymp'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_lymp'] / 100)\
                    .quantize(Decimal('10.00'))
            if cleaned_data['p_mono']:
                cleaned_data['mono'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_mono'] / 100)\
                    .quantize(Decimal('10.00'))
            if cleaned_data['p_eo']:
                cleaned_data['p_eo'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_eo'] / 100)\
                    .quantize(Decimal('10.00'))
            if cleaned_data['p_baso']:
                cleaned_data['p_baso'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_baso'] / 100)\
                    .quantize(Decimal('10.00'))

        return cleaned_data


class DataClassificationForm(DataAugmentedForm):
    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'unit_ii', 'uuid', 'timestamp', 'is_covid19'
        ]

    def clean(self):
        cleaned_data = super().clean()

        hemogram_fields_count = 0
        threshold = getattr(settings, 'HEMOGRAM_FIELDS_MIN_NUM_SUBMIT', 6)
        for hfield in self.Meta.model.HEMOGRAM_FIELDS + self.PERCENTAGE_FIELDS:
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


class DataInputForm(DataAugmentedForm):
    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'uuid', 'timestamp',
        ]
