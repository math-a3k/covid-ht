#
from django.utils.translation import gettext_lazy as _

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from data.serializers import DataClassificationSerializer

from ..utils import (get_current_classifier, classification_tuple, )


class Classify(generics.GenericAPIView):
    """
    Endpoint for classifying data.
    """
    serializer_class = DataClassificationSerializer

    def post(self, request, format=None):
        """
        Return the result of classification if data submitted is valid.
        """
        classifier = get_current_classifier()
        if classifier:
            serializer = DataClassificationSerializer(data=request.data)
            if serializer.is_valid(raise_exception=False):
                (result, result_prob) = classification_tuple(
                    classifier, serializer.data
                )
                if result:
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
