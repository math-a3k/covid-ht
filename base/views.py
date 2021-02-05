#
from django.conf import settings
from django.shortcuts import render

from data.forms import DataClassificationForm

from .utils import (classification_tuple, get_current_classifier)


def home(request):
    classifier = get_current_classifier()
    example_data = getattr(settings, "EXAMPLE_DATA", False)
    if request.method == 'POST':
        dataform = DataClassificationForm(request.POST)
        if dataform.is_valid():
            (result, result_prob) = classification_tuple(
                    classifier, dataform.cleaned_data
                )
        else:
            result = None
            result_prob = None
    else:
        dataform = DataClassificationForm()
        result = None
        result_prob = None

    return render(
        request,
        'base/home.html',
        {
            'classifier': classifier,
            'example_data': example_data,
            'dataform': dataform,
            'result': result,
            'result_prob': result_prob
        }
    )


def about(request):
    return render(
        request,
        'base/about.html',
        {}
    )
