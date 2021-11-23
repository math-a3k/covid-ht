from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import BooleanField
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import Data


class NullableBooleanField(BooleanField):
    default_empty_html = None
    initial = None


class UseNullableBooleanFieldMixin(object):
    serializer_field_mapping = \
        serializers.ModelSerializer.serializer_field_mapping
    serializer_field_mapping[models.BooleanField] = NullableBooleanField
    serializer_field_mapping[models.NullBooleanField] = NullableBooleanField


class PublicDataSerializer(UseNullableBooleanFieldMixin,
                           serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Data
        fields = [
            'chtuid', 'unit', 'timestamp', 'uuid', model.LEARNING_LABELS
            ] + model.get_main_fields()

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


class ModelValidatedModelSerializer(UseNullableBooleanFieldMixin,
                                    serializers.ModelSerializer):

    def validate(self, data):
        model_obj = self.Meta.model(**data)
        try:
            model_obj.clean()
            for field in model_obj._meta.fields:
                field_value = getattr(model_obj, field.attname, None)
                if field_value:
                    data[field.attname] = field_value
        except DjangoValidationError as exc:
            drf_error = DRFValidationError(
                detail=serializers.as_serializer_error(exc)
            )
            raise drf_error
        return data


class DataClassificationSerializer(ModelValidatedModelSerializer):
    class Meta:
        model = Data
        exclude = [
            'id', 'unit', 'user', 'unit_ii', 'uuid', 'timestamp', 'is_covid19',
            'is_finished',
        ]

    def validate(self, data):
        cleaned_data = super().validate(data)
        clinical_fields_count = 0
        threshold = getattr(settings, 'CLINICAL_FIELDS_MIN_NUM_SUBMIT', 6)
        clinical_fields = self.Meta.model.get_main_fields() + \
            self.Meta.model.get_conversion_fields()
        for field in clinical_fields:
            if cleaned_data.get(field, None):
                clinical_fields_count += 1
        if clinical_fields_count < threshold:
            raise serializers.ValidationError(
                _("At least %(threshold)s clinical fields must be "
                  "submitted in order to classify a clinical result." %
                    {'threshold': threshold}),
                code="not_enough_fields",
            )
        return cleaned_data


class DatasetClassificationSerializer(serializers.Serializer):
    dataset = serializers.ListField(child=DataClassificationSerializer())


class DataInputSerializer(ModelValidatedModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Data
        exclude = [
            'unit', 'user',
        ]

    def get_url(self, obj):
        return reverse('rest-api:data-ru', args=[obj.uuid, ])


class DataShareSerializer(serializers.ModelSerializer):

    class Meta:
        model = Data
        exclude = ['id', 'user', 'unit', 'unit_ii', ]
