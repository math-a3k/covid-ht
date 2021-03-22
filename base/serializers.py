from rest_framework import serializers

from data.models import Data


class DataShareSerializer(serializers.ModelSerializer):

    class Meta:
        model = Data
        exclude = ['id', 'user', 'unit', 'unit_ii', ]
