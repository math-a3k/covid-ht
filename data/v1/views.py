#

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    BasePermission, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from ..models import Data
from ..serializers import (DataInputSerializer, DataListSerializer, )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 10000


class IsOwnerEditOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class DataListCreate(generics.ListCreateAPIView):
    queryset = Data.objects.all()
    serializer_class = DataInputSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            unit=self.request.user.unit
        )

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DataListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DataListSerializer(queryset, many=True)
        return Response(serializer.data)

    def paginate_queryset(self, queryset):
        if self.paginator and \
                self.request.query_params.get(
                    self.paginator.page_query_param, None) == 'no':
            return None
        return super().paginate_queryset(queryset)


class DataReadUpdate(generics.RetrieveUpdateAPIView):
    queryset = Data.objects.all()
    serializer_class = DataInputSerializer
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerEditOnly]
