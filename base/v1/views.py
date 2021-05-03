from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from data.serializers import (
    DataClassificationSerializer, DatasetClassificationSerializer
)
from data.models import Data

from ..models import CurrentClassifier


class Classify(generics.GenericAPIView):
    """
    Endpoint for classifying data (single observation).
    """
    serializer_class = DataClassificationSerializer
    use_network = False
    _classifier = None

    def get_data(self, serializer):
        data = Data.apply_conversion_fields_rules_to_dict(
            serializer.validated_data
        )
        return data

    def get_classifier(self):
        if not self._classifier:
            self._classifier = CurrentClassifier.objects.last()
        return self._classifier

    def predict(self, data):
        if self.use_network:
            return self.get_classifier().network_predict(data)
        else:
            return self.get_classifier().predict(data) + (None, )

    def post(self, request, format=None):
        """
        Return the result of classification if data submitted is valid.
        """
        self.use_network = \
            self.request.GET.get('use_network', False) in ["True", "true"]
        if self.get_classifier():
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                (result, result_prob, votes) = \
                    self.predict(self.get_data(serializer))
                response_content = {'result': result, 'prob': result_prob}
                if self.use_network:
                    response_content['votes'] = votes
                return Response(response_content, status=status.HTTP_200_OK)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
                    {'detail': _("Classification Unavailable")},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

    def get(self, request, format=None):
        if self.get_classifier():
            metadata = self.get_classifier().get_local_classifier().metadata
            metadata["chtuid"] = settings.CHTUID
            return Response(metadata, status=status.HTTP_200_OK)
        return Response(
                    {'detail': _("Classification Unavailable")},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )


class ClassifyDataset(Classify):
    """
    Endpoint for classifying datasets (multiple observations).
    """
    serializer_class = DatasetClassificationSerializer

    def get_data(self, serializer):
        data = []
        for s_vd in serializer.validated_data['dataset']:
            d = Data.apply_conversion_fields_rules_to_dict(s_vd)
            data.append(d)
        return data
