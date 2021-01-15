#
from rest_framework_csv.renderers import CSVRenderer

from .serializers import UnitDataSerializer


class UnitCSVRenderer(CSVRenderer):
    header = [field for field in UnitDataSerializer().fields]
