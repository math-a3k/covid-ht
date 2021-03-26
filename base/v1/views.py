#
from django.utils.translation import gettext_lazy as _

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from data.serializers import (
    DataClassificationSerializer, DatasetClassificationSerializer
)

from ..models import CurrentClassifier


class Classify(generics.GenericAPIView):
    """
    Endpoint for classifying data (single observation).
    """
    serializer_class = DataClassificationSerializer
    _classifier = None

    def get_data(self, serializer):
        return serializer.data

    def get_classifier(self):
        if not self._classifier:
            self._classifier = CurrentClassifier.objects.last()
        return self._classifier

    def predict(self, data):
        return self.get_classifier().predict(data, include_scores=True)

    def post(self, request, format=None):
        """
        Return the result of classification if data submitted is valid.
        """
        if self.get_classifier():
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                (result, result_prob) = self.predict(self.get_data(serializer))
                return Response(
                    {'result': result, 'prob': result_prob},
                    status=status.HTTP_200_OK
                )
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
            return Response(
                    self.get_classifier().get_local_classifier().metadata,
                    status=status.HTTP_200_OK
                )
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
        return serializer.data['dataset']
