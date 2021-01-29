#
from decimal import Decimal

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from .models import Data


class PublicDataSerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Data
        exclude = ['user', 'unit_ii', ]

    def get_unit(self, obj):
        return obj.unit.pk

    def get_timestamp(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M")


class DataListSerializer(PublicDataSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Data
        exclude = ['user', 'unit_ii', ]

    def get_url(self, obj):
        return reverse('rest-api:data-ru', args=[obj.uuid, ])


class BaseInputDataSerializer(serializers.ModelSerializer):
    PERCENTAGE_FIELDS = ['p_neut', 'p_lymp', 'p_mono', 'p_eo', 'p_baso']

    p_neut = serializers.DecimalField(
        label=_("NEUT (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Neutrophils (% of White Blood Cells)'),
        min_value=0.0, max_value=99.9
    )
    p_lymp = serializers.DecimalField(
        label=_("LYMPH (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Lymphocytes (% of White Blood Cells)'),
        min_value=0.0, max_value=99.9
    )
    p_mono = serializers.DecimalField(
        label=_("MONO (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Monocytes (% of White Blood Cells)'),
        min_value=0.0, max_value=99.9
    )
    p_eo = serializers.DecimalField(
        label=_("EO (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Eosinophils (% of White Blood Cells)'),
        min_value=0.0, max_value=99.9
    )
    p_baso = serializers.DecimalField(
        label=_("BASO (% WBC)"),
        max_digits=4, decimal_places=2,
        required=False,
        help_text=_('Basophils (% of White Blood Cells)'),
        min_value=0.0, max_value=99.9
    )

    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'uuid', 'timestamp',
        ]

    def validate(self, data):
        cleaned_data = super().validate(data)
        for field in self.PERCENTAGE_FIELDS:
            if cleaned_data.get(field, None) \
                    and not cleaned_data.get('wbc', None):
                raise serializers.ValidationError(
                    _("WBC must be present in order to use percentage "
                      "fields."),
                    code="wbc_not_present",
                )
        # Convert to absolute values in the correspondent field
        if cleaned_data.get('wbc', None):
            if cleaned_data.get('p_neut', None):
                cleaned_data['neut'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_neut'] / 100)\
                    .quantize(Decimal('10.00'))
                cleaned_data.pop('p_neut')
            if cleaned_data.get('p_lymp', None):
                cleaned_data['lymp'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_lymp'] / 100)\
                    .quantize(Decimal('10.00'))
                cleaned_data.pop('p_lymp')
            if cleaned_data.get('p_mono', None):
                cleaned_data['mono'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_mono'] / 100)\
                    .quantize(Decimal('10.00'))
                cleaned_data.pop('p_mono')
            if cleaned_data.get('p_eo', None):
                cleaned_data['eo'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_eo'] / 100)\
                    .quantize(Decimal('10.00'))
                cleaned_data.pop('p_eo')
            if cleaned_data.get('p_baso', None):
                cleaned_data['baso'] = \
                    (cleaned_data['wbc'] * cleaned_data['p_baso'] / 100)\
                    .quantize(Decimal('10.00'))
                cleaned_data.pop('p_baso')

        return cleaned_data


class DataClassificationSerializer(BaseInputDataSerializer):
    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'unit_ii', 'uuid', 'timestamp', 'is_covid19'
        ]

    def validate(self, data):
        cleaned_data = super().validate(data)

        hemogram_fields_count = 0
        threshold = getattr(settings, 'HEMOGRAM_FIELDS_MIN_NUM_SUBMIT', 6)
        for hfield in self.Meta.model.HEMOGRAM_FIELDS + self.PERCENTAGE_FIELDS:
            if cleaned_data.get(hfield, None):
                hemogram_fields_count += 1
        if hemogram_fields_count < threshold:
            raise serializers.ValidationError(
                _("At least %(threshold)s hemogram result fields must be "
                  "submitted in order to classify an hemogram." %
                    {'threshold': threshold}),
                code="not_enough_fields",
            )
        return cleaned_data


class DataInputSerializer(BaseInputDataSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Data
        exclude = [
            'unit', 'user', 'timestamp',
        ]
        extra_kwargs = {
            'uuid': {'read_only': True},
            'unit_ii': {'write_only': True},
        }

    def get_url(self, obj):
        return reverse('rest-api:data-ru', args=[obj.uuid, ])
