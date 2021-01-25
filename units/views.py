#
from django.contrib.auth.decorators import (login_required, user_passes_test)
from django.contrib.auth.forms import SetPasswordForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import (Count, Max)
from django.http import Http404
from django.shortcuts import (get_object_or_404, redirect, render, )
# from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from rest_framework import generics

from base.models import User
from data.models import Data

from .forms import (UnitUserChangeForm, UnitUserCreationForm, UnitEditForm)
from .models import Unit
from .renderers import UnitCSVRenderer
from .serializers import UnitDataSerializer


# -> Units (public)

def list(request):
    page = request.GET.get('page', 1)
    units = Unit.objects\
        .annotate(data_amount=Count('data'))\
        .annotate(last_updated=Max('data__timestamp'))\
        .order_by("id")

    # Pagination
    paginator = Paginator(units, 50)
    try:
        units = paginator.page(page)
    except PageNotAnInteger:  # pragma: no cover
        units = paginator.page(1)
    except EmptyPage:  # pragma: no cover
        units = paginator.page(paginator.num_pages)

    return render(
        request,
        'units/list.html',
        {
            'units': units,
        }
    )


def detail(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    members_di_size = unit.users.filter(user_type=User.DATA).count()
    members_m_size = unit.users.filter(user_type=User.MANAGER).count()
    data_size = unit.data.count()
    data_last = Data.objects.last()
    if data_last:
        data_last_updated = data_last.timestamp
    else:
        data_last_updated = None
    return render(
        request,
        'units/detail.html',
        {
            'unit': unit,
            'members_di_size': members_di_size,
            'members_m_size': members_m_size,
            'data_size': data_size,
            'data_last_updated': data_last_updated
        }
    )


# -> Unit (Curent)

@login_required
def unit_dashboard(request):
    unit = request.user.unit
    if unit:
        members_di_size = unit.users.filter(user_type=User.DATA).count()
        members_m_size = unit.users.filter(user_type=User.MANAGER).count()
        data_size = unit.data.count()
        data_last = Data.objects.last()
        if data_last:
            data_last_updated = data_last.timestamp
        else:
            data_last_updated = None
    else:
        members_di_size = None
        members_m_size = None
        data_size = None
        data_last_updated = None

    return render(
        request,
        'units/dashboard.html',
        {
            'unit': unit,
            'members_di_size': members_di_size,
            'members_m_size': members_m_size,
            'data_size': data_size,
            'data_last_updated': data_last_updated
        }
    )


@login_required
@user_passes_test(lambda u: u.is_manager)
def unit_edit(request):
    if request.method == 'POST':
        form = UnitEditForm(request.POST, instance=request.user.unit)
        if form.is_valid():
            form.save()
            return redirect("units:current:dashboard")
    else:
        form = UnitEditForm(instance=request.user.unit)

    return render(
        request,
        'units/edit.html',
        {
            'form': form,
        }
    )


@login_required
def unit_users_list(request):
    users = User.objects.filter(unit=request.user.unit)
    return render(
        request,
        'units/users_list.html',
        {
            'users': users,
        }
    )


@login_required
def unit_users_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user.unit != user.unit:
        raise Http404()
    return render(
        request,
        'units/users_detail.html',
        {
            'user': user,
        }
    )


@login_required
def unit_users_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if (not request.user.user_type == User.MANAGER and request.user != user) \
            or request.user.unit != user.unit:
        raise Http404()
    if request.method == 'POST':
        form = UnitUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("units:current:users-detail", user.pk)
    else:
        form = UnitUserChangeForm(instance=user)

    return render(
        request,
        'units/users_edit.html',
        {
            'form': form,
            'user': user,
        }
    )


@login_required
@user_passes_test(lambda u: u.is_manager)
def unit_users_new(request):
    if request.method == 'POST':
        form = UnitUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.unit = request.user.unit
            user.save()
            return redirect("units:current:users-detail",  user.pk)
    else:
        form = UnitUserCreationForm()

    return render(
        request,
        'units/users_new.html',
        {
            'form': form,
        }
    )


@login_required
def unit_users_set_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    if (not request.user.user_type == User.MANAGER and request.user != user) \
            or request.user.unit != user.unit:
        raise Http404()
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("units:current:users-detail", user.pk)
    else:
        form = SetPasswordForm(user)

    return render(
        request,
        'units/users_set_password.html',
        {
            'user': user,
            'form': form,
        }
    )


@login_required
def unit_data(request):
    page = request.GET.get('page', 1)
    data = Data.objects.filter(unit=request.user.unit).select_related("user")

    # Pagination
    paginator = Paginator(data, 20)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:  # pragma: no cover
        data = paginator.page(1)
    except EmptyPage:  # pragma: no cover
        data = paginator.page(paginator.num_pages)

    fields_all = Data._meta.get_fields()
    fields_excluded = ['id', 'unit_id', 'user_id', 'uuid']
    fields = [
        field for field in fields_all if field.attname not in fields_excluded
    ]
    rows = Data.objects.count()
    cols = len(fields)
    if rows:
        last_updated = Data.objects.last().timestamp
    else:
        last_updated = None
    return render(
        request,
        'units/data.html',
        {
            'data': data,
            'fields': fields,
            'rows': rows,
            'cols': cols,
            'last_updated': last_updated
        }
    )


class CSV(generics.ListAPIView):
    renderer_classes = (UnitCSVRenderer, )
    serializer_class = UnitDataSerializer
    queryset = Data.objects.all()

    def get_queryset(self):
        return Data.objects.filter(unit=self.request.user.unit)\
            .select_related("user")

    def finalize_response(self, request, response, *args, **kwargs):
        response['Content-Disposition'] = \
            "attachment; filename=covid-ht-unit-{1}-data-{0}UTC.csv".format(
                timezone.now().utcnow().strftime("%Y%m%dT%I%M"),
                self.request.user.unit.pk
            )
        return super().finalize_response(request, response, *args, **kwargs)
