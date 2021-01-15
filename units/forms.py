#
from django import forms
from django.contrib.auth.forms import (UserChangeForm, UserCreationForm)
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _

from base.models import User
from .models import Unit


class UnitUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = (
            'user_type', 'first_name', 'last_name', 'username',
            'email', 'cellphone',
        )


class UnitUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'user_type', 'first_name', 'last_name', 'username',
            'email', 'cellphone', 'password1', 'password2'
        )


class UnitEditForm(forms.ModelForm):
    class Meta:
        model = Unit
        exclude = ('timestamp', 'is_active',)
