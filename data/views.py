#
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import (get_object_or_404, redirect, render, )
from django.utils import timezone
from django.utils.decorators import method_decorator
# from django.utils.translation import gettext_lazy as _
from rest_framework import generics

from .forms import (DataInputForm, )
from .models import Data
from .renderers import PublicCSVRenderer
from .serializers import PublicDataSerializer
from .v1.views import DataPrivacyMode


def is_not_allowed_in_data_privacy_mode(function):
    actual_decorator = user_passes_test(
        lambda u:
        False if settings.DATA_PRIVACY_MODE and u.is_anonymous else True
    )
    if function:
        return actual_decorator(function)
    return actual_decorator  # pragma: no cover


@is_not_allowed_in_data_privacy_mode
def public_list(request):
    page = request.GET.get('page', 1)
    data_qs = Data.objects.filter(is_finished=True).order_by("-timestamp")

    # Pagination
    paginator = Paginator(data_qs, 50)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:  # pragma: no cover
        data = paginator.page(1)
    except EmptyPage:  # pragma: no cover
        data = paginator.page(paginator.num_pages)

    fields_all = list(Data._meta.fields)
    fields_excluded = [
        'id', 'user_id', 'unit_ii', 'timestamp', 'unit', 'uuid',
    ]
    fields = [
        field for field in fields_all if field.attname not in fields_excluded
    ]
    rows = data_qs.count()
    cols = len(fields)
    if rows:
        last_updated = Data.objects.last().timestamp
    else:
        last_updated = None
    return render(
        request,
        'data/public_list.html',
        {
            'data': data,
            'fields': fields,
            'rows': rows,
            'cols': cols,
            'last_updated': last_updated
        }
    )


class CSV(generics.ListAPIView):
    renderer_classes = (PublicCSVRenderer, )
    serializer_class = PublicDataSerializer
    queryset = Data.objects.filter(is_finished=True)
    permission_classes = [DataPrivacyMode, ]

    def finalize_response(self, request, response, *args, **kwargs):
        response['Content-Disposition'] = \
            "attachment; filename=covid-ht-data-{0}UTC.csv".format(
                timezone.now().utcnow().strftime("%Y%m%dT%I%M")
            )
        return super().finalize_response(request, response, *args, **kwargs)


@is_not_allowed_in_data_privacy_mode
def detail(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    return render(
        request,
        'data/detail.html',
        {
            'data': data,
        }
    )


@login_required
def edit(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    if not request.user == data.user:
        raise Http404()
    if request.method == 'POST':
        dataform = DataInputForm(request.POST, instance=data)
        if dataform.is_valid():
            data = dataform.save(commit=False)
            data.timestamp = timezone.now()
            data.save()
            return redirect("units:current:data")
    else:
        dataform = DataInputForm(instance=data)

    return render(
        request,
        'data/edit.html',
        {
            'data': data,
            'dataform': dataform,
        }
    )


@login_required
def input(request):
    if request.method == 'POST':
        dataform = DataInputForm(request.POST)
        if dataform.is_valid():
            data = dataform.save(commit=False)
            data.user = request.user
            data.unit = request.user.unit
            data.save()
            if '_addanother' in dataform.data:
                return redirect("data:input")
            else:
                return redirect("units:current:data")
    else:
        dataform = DataInputForm()

    return render(
        request,
        'data/input.html',
        {
            'dataform': dataform,
        }
    )
