from django.conf import settings
from django.http import Http404

from rest_framework import generics
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    BasePermission, IsAuthenticatedOrReadOnly, SAFE_METHODS
)
from rest_framework.request import clone_request
from rest_framework.response import Response

from ..models import Data
from ..serializers import (DataInputSerializer, DataListSerializer, )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 10000


class IsOwnerOrReadOnly(BasePermission):
    # https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class NetworkPUTAsCreateMixin(object):
    """
    The following mixin class supports PUT-as-create for data sharing between
    covid-ht nodes. Data is propagated through the nodes by PUT requests, which
    creates or updates the records and ignores the request if the chtuid is the
    same as the current node.
    (from https://gist.github.com/tomchristie/a2ace4577eff2c603b1b)
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object_or_none()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)

        if instance is None:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.perform_update(serializer):
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_208_ALREADY_REPORTED)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def get_object_or_none(self):
        try:
            return self.get_object()
        except Http404:
            if self.request.method == 'PUT':
                # For PUT-as-create operation, we need to ensure that we have
                # relevant permissions, as if this was a POST request.  This
                # will either raise a PermissionDenied exception, or simply
                # return None.
                self.check_permissions(clone_request(self.request, 'POST'))
            else:
                # PATCH requests where the object does not exist should still
                # return a 404 response.
                raise

    def get_object(self):
        queryset = self.get_queryset()
        filter = {
            self.lookup_field: self.request.data.get(self.lookup_field, None)
        }
        obj = generics.get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj


class DataListCreateUpdate(
        NetworkPUTAsCreateMixin, generics.UpdateAPIView,
        generics.ListCreateAPIView):
    queryset = Data.objects.all()
    serializer_class = DataInputSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    lookup_field = 'uuid'

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            unit=self.request.user.unit
        )

    def perform_update(self, serializer):
        if not serializer.validated_data['chtuid'] == settings.CHTUID:
            serializer.save(
                user=self.request.user,
                unit=self.request.user.unit
            )
            return True
        return False

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
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
