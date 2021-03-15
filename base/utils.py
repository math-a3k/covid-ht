#
from django.utils.translation import gettext_lazy as _

from .models import CurrentClassifier


def get_current_classifier(internal=False):
    cc = CurrentClassifier.objects.last()
    if cc:
        return (
            cc.external if cc.external and not internal
            else cc.classifier._get_technique()
        )
    return None


def classification_tuple(classifier, data):
    if classifier.is_inferred:
        if hasattr(classifier, 'service_url'):
            result = classifier.predict(data)
            return (result['result'], result['prob'])
        else:
            (res, res_prob) = \
                classifier.predict([data], include_scores=True)
            result = _("Positive") if res[0] else _("Negative")
            return (result.upper(), res_prob)
    return (None, None)
