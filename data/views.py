#
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (get_object_or_404, redirect, render, )
# from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from rest_framework import generics

from .forms import (DataInputForm, )
from .models import Data
from .renderers import PublicCSVRenderer
from .serializers import PublicDataSerializer


def public_list(request):
    page = request.GET.get('page', 1)
    data = Data.objects.all().order_by("-timestamp")

    # Pagination
    paginator = Paginator(data, 50)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    fields_all = list(Data._meta.fields)
    fields_excluded = ['id', 'user_id', 'unit_ii', 'timestamp']
    fields = [
        field for field in fields_all if field.attname not in fields_excluded
    ]
    rows = Data.objects.count()
    cols = len(fields)
    last_updated = Data.objects.last().timestamp
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
    queryset = Data.objects.all()

    def finalize_response(self, request, response, *args, **kwargs):
        response['Content-Disposition'] = \
            "attachment; filename=covid-ht-data-{0}UTC.csv".format(
                timezone.now().utcnow().strftime("%Y%m%dT%I%M")
            )
        return super().finalize_response(request, response, *args, **kwargs)


@login_required
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
