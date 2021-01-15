#
from rest_framework_csv.renderers import CSVRenderer

from .serializers import PublicDataSerializer


class PublicCSVRenderer(CSVRenderer):
    header = [field for field in PublicDataSerializer().fields]
