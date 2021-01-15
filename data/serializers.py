#
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
