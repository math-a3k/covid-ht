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
            try:
                (result, result_prob) = classification_tuple(
                            classifier, dataform.cleaned_data
                        )
                classifier_error = None
            except Exception as e:
                (result, result_prob) = None, None
                classifier_error = str(e)
        else:
            (result, result_prob, classifier_error) = None, None, None
    else:
        dataform = DataClassificationForm()
        (result, result_prob, classifier_error) = None, None, None

    return render(
        request,
        'base/home.html',
        {
            'classifier': classifier,
            'classifier_error': classifier_error,
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
