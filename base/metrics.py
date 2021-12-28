from sklearn.metrics._classification import confusion_matrix
from sklearn.metrics import make_scorer


def specificity_score(
        y_true,
        y_pred,
        *,
        labels=None,
        sample_weight=None,
        normalize='all'
):
    """
    Computes the specificity for a binary classification / prediction.

    tn: True Negatives
    fp: False Positives
    fn: False Negatives
    tp: True Positives

    specificity = tn / (tn + fn)
    """
    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        sample_weight=sample_weight,
        normalize=normalize
    ).ravel()
    denom = (tn + fn)
    if denom == 0:  # Avoid division by zero
        denom = 1
    return tn / denom

METRICS = {
    'specificity': make_scorer(specificity_score)
}
