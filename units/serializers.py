#
from rest_framework import serializers

from data.models import Data


class UnitDataSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Data
        exclude = ['uuid', 'unit'] + model.CONVERSION_FIELDS

    def get_user(self, obj):
        return obj.user.name

    def get_timestamp(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M")
