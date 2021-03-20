#
from django.utils.translation import gettext_lazy as _

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from data.serializers import DataClassificationSerializer

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



    def post(self, request, format=None):
        """
        Return the result of classification if data submitted is valid.
        """
        classifier = get_current_classifier(internal=True)
        if classifier:
            serializer = DataClassificationSerializer(data=request.data)
            if serializer.is_valid():
                (result, result_prob) = classification_tuple(
                    classifier, serializer.data
                )
                return Response(
                    {'result': result, 'prob': result_prob[0]},
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
