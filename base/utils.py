#
from django.utils.translation import gettext_lazy as _

from .models import CurrentClassifier


def get_current_classifier():
    cc = CurrentClassifier.objects.last()
    if cc:
        return cc.classifier
    return None


def classification_tuple(classifier, data):
    if classifier.is_inferred:
        (res, res_prob) = \
            classifier.predict([data], include_probs=True)
        result = _("Positive") if res[0] else _("Negative")
        result_prob = res_prob[0][1] if res[0] else res_prob[0][0]
        return (result.upper(), result_prob)
    return (None, None)
