#
from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from data.forms import DataClassificationForm

from .models import CurrentClassifier


def get_current_classifier():
    cc = CurrentClassifier.objects.last()
    if cc:
        return cc.classifier
    return None


def home(request):
    classifier = get_current_classifier()
    example_data = getattr(settings, "EXAMPLE_DATA", False)
    if request.method == 'POST':
        dataform = DataClassificationForm(request.POST)
        if dataform.is_valid():
            (res, res_prob) = \
                classifier.predict([dataform.cleaned_data], include_probs=True)
            result = _("Positive") if res[0] else _("Negative")
            result_prob = res_prob[0][1] if res[0] else res_prob[0][0]
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
