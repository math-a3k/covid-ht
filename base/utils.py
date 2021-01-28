#
from .models import CurrentClassifier


def get_current_classifier():
    cc = CurrentClassifier.objects.last()
    if cc:
        return cc.classifier
    return None
