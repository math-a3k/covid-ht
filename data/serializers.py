#

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import Data


class PublicDataSerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Data
        fields = [
            'chtuid', 'unit', 'timestamp', 'uuid', model.LEARNING_LABELS
            ] + model.get_hemogram_main_fields()

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


class ModelValidatedModelSerializer(serializers.ModelSerializer):

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
            'is_finished'
        ]

    def validate(self, data):
        cleaned_data = super().validate(data)
        hemogram_fields_count = 0
        threshold = getattr(settings, 'HEMOGRAM_FIELDS_MIN_NUM_SUBMIT', 6)
        fields = self.Meta.model.get_hemogram_main_fields() + \
            self.Meta.model.get_conversion_fields()
        for hfield in fields:
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


class DatasetClassificationSerializer(serializers.Serializer):
    dataset = serializers.ListField(child=DataClassificationSerializer())


class DataInputSerializer(ModelValidatedModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Data
        exclude = [
            'unit', 'user',  # 'timestamp',
        ]
        # extra_kwargs = {
        #     'uuid': {'read_only': True},
        #     'unit_ii': {'write_only': True},
        # }

    def get_url(self, obj):
        return reverse('rest-api:data-ru', args=[obj.uuid, ])


class DataShareSerializer(serializers.ModelSerializer):

    class Meta:
        model = Data
        exclude = ['id', 'user', 'unit', 'unit_ii', ]
