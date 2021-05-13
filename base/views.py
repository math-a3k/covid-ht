from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
# from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render
from django.views.generic import RedirectView
from django.utils.translation import ugettext_lazy as _

from data.forms import DataClassificationForm
from data.models import Data

from .models import CurrentClassifier, ExternalClassifier, NetworkNode


def home(request):
    classifier = CurrentClassifier.objects.last()
    nodes = NetworkNode.objects.filter(classification_request=True)
    example_data = getattr(settings, "EXAMPLE_DATA_V2", False)
    chtuid = getattr(settings, "CHTUID", "-")
    (result, result_prob, votes, classifier_error) = None, None, None, None
    if request.method == 'POST':
        dataform = DataClassificationForm(request.POST)
        if dataform.is_valid():
            data = Data.apply_conversion_fields_rules_to_dict(
                dataform.cleaned_data
            )
            try:
                (result, result_prob, votes) = classifier.network_predict(data)
                result = result[0]
                result_prob = result_prob[0]
            except Exception as e:
                classifier_error = str(e)
    else:
        dataform = DataClassificationForm()

    return render(
        request,
        'base/home.html',
        {
            'classifier': classifier,
            'nodes': nodes,
            'classifier_error': classifier_error,
            'example_data': example_data,
            'chtuid': chtuid,
            'dataform': dataform,
            'result': result,
            'result_prob': result_prob,
            'votes': votes
        }
    )


def about(request):
    return render(
        request,
        'base/about.html',
        {}
    )


class UpdateMetadataView(UserPassesTestMixin, RedirectView):
    """
    Updates metadata for External Classifiers
    """
    permanent = False

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_redirect_url(self, *args, **kwargs):
        ec = get_object_or_404(ExternalClassifier, pk=kwargs['pk'])
        updated = ec.update_metadata()
        if updated:
            messages.success(self.request,
                             _("Success at updating metadata"))
        else:
            messages.error(self.request,
                           _("Errors ocurred while updating metadata, check "
                             "network error logs"))
        return self.request.META.get('HTTP_REFERER', '/')
