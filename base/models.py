from numpy import mean
import requests
from sklearn import metrics as sklearn_metrics

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_ai.supervised_learning.models import HGBTreeClassifier, SVC
from rest_framework import status

from data.models import Data
from data.serializers import DataClassificationSerializer, DataShareSerializer


class User(AbstractUser):
    """
    Custom User Model for covid-ht
    """
    MANAGER = 0
    DATA = 1

    USER_TYPE_CHOICES = (
        (MANAGER, _("Manager of Unit")),
        (DATA, _("Data Input")),
    )

    user_type = models.PositiveSmallIntegerField(
        _("User Type"),
        choices=USER_TYPE_CHOICES, default=DATA
    )
    unit = models.ForeignKey(
        "units.Unit",
        on_delete=models.PROTECT,
        verbose_name=_("Unit"),
        blank=True, null=True,
        related_name='users'
    )
    cellphone = models.CharField(
        _("Cellphone"),
        max_length=50,
        blank=True, null=True,
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def url(self):
        return(reverse('units:current:users-detail', args=[self.pk]))

    @property
    def name(self):
        return "{0} {1}".format(
            self.first_name.upper(), self.last_name.upper()
        )

    @property
    def is_manager(self):
        return (self.user_type == self.MANAGER) \
            or self.is_superuser or self.is_staff

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.upper()
        self.last_name = self.last_name.upper()
        super().save(*args, **kwargs)


class CurrentClassifier(models.Model):
    """
    Singleton Model for selecting which classifier should be used
    """
    NETWORK_VOTING_DISABLED = 0
    NETWORK_VOTING_MAJORITY = 1
    NETWORK_VOTING_MIN_POSITIVE = 2
    NETWORK_VOTING_MIN_NEGATIVE = 3

    NETWORK_VOTING_CHOICES = (
        (NETWORK_VOTING_DISABLED, _("No Network Voting")),
        (NETWORK_VOTING_MAJORITY, _("Majority")),
        (NETWORK_VOTING_MIN_POSITIVE, _("Minimum of Postives")),
        (NETWORK_VOTING_MIN_NEGATIVE, _("Minimum of Negatives")),
    )

    classifier = models.OneToOneField(
        'supervised_learning.SupervisedLearningTechnique',
        on_delete=models.PROTECT,
        related_name='current_classifier',
        blank=True, null=True
    )
    external = models.OneToOneField(
        'base.ExternalClassifier',
        on_delete=models.PROTECT,
        related_name='current_classifier',
        blank=True, null=True
    )
    network_voting = models.PositiveSmallIntegerField(
        _("Network Voting Policy"),
        choices=NETWORK_VOTING_CHOICES, default=NETWORK_VOTING_DISABLED
    )
    network_voting_threshold = models.PositiveSmallIntegerField(
        _("Network Voting Threshold"),
        blank=True, null=True,
        help_text=_(
            "Only applicable for Minimum Positives / Negatives voting "
            "policies."
        )
    )

    class Meta:
        verbose_name = _("Current Classifier")

    def __str__(self):
        return str(self.classifier)

    def get_local_classifier(self, internal=False):
        if self.external and not internal:
            return self.external
        else:
            return self.classifier._get_technique()

    def predict(self, observations, include_scores=True, internal=False):
        local_classifier = self.get_local_classifier(internal=internal)
        if not isinstance(observations, list):
            observations = [observations]
        if local_classifier.is_inferred:
            if hasattr(local_classifier, 'service_url'):
                result = local_classifier.predict(observations)
                return (result['result'], result['prob'])
            else:
                (res, scores) = \
                    local_classifier.predict(
                        observations, include_scores=include_scores)
                results = ["POSITIVE" if r else "NEGATIVE" for r in res]
                if len(results) == 1:
                    return (results[0], scores[0])
                else:
                    return (results, scores)
        return (None, None)

    def network_predict(self, observation):
        if self.network_voting == self.NETWORK_VOTING_DISABLED:
            return None
        votes = self._get_network_votes(observation)
        votes_positive = [
            node for node in votes if votes[node]["result"] == "POSITIVE"
        ]
        votes_negative = [
            node for node in votes if votes[node]["result"] == "NEGATIVE"
        ]
        scores_positive = [
            votes[node]["prob"] for node in votes if node in votes_positive
        ]
        scores_negative = [
            votes[node]["prob"] for node in votes if node in votes_negative
        ]
        if self.network_voting == self.NETWORK_VOTING_MAJORITY:
            if len(votes_positive) > len(votes_negative):
                return ("POSITIVE", mean(scores_positive))
            if len(votes_positive) < len(votes_negative):
                return ("NEGATIVE", mean(scores_negative))
            if "local" in votes_positive:
                return ("POSITIVE", mean(scores_positive))
            return ("NEGATIVE", mean(scores_negative))
        elif self.network_voting == self.NETWORK_VOTING_MIN_NEGATIVE:
            if len(votes_negative) >= self.network_voting_threshold:
                return ("NEGATIVE", mean(scores_negative))
            return ("POSITIVE", mean(scores_positive))
        else:  # self.network_voting == self.NETWORK_VOTING_MIN_POSITIVE:
            if len(votes_positive) >= self.network_voting_threshold:
                return ("POSITIVE", mean(scores_positive))
            return ("NEGATIVE", mean(scores_negative))

    def _get_network_votes(self, observation):
        votes = {}
        local_vote = self.predict(observation, internal=True)
        votes["local"] = {"result": local_vote[0], "prob": local_vote[1]}
        for node in NetworkNode.objects.filter(classification_request=True):
            try:
                votes[node.name] = node.predict(observation)
            except Exception:
                pass
        return votes

    def clean(self):
        if not self.classifier and not self.external:
            raise ValidationError(
                _("Both classifier and external can't be null")
            )


class ExternalClassifier(models.Model):
    _requests_client = requests

    name = models.CharField(
        _("Name"),
        max_length=100
    )
    service_url = models.URLField(
        _("Service URL"),
        default="http://localhost"
    )
    remote_user = models.CharField(
        _("Remote User"),
        max_length=50, blank=True, null=True,
        help_text=_(
            "Username in the External Service for making requests"
        )
    )
    remote_user_token = models.CharField(
        _("Remote User Token"),
        max_length=250, blank=True, null=True,
        help_text=_(
            "Token for authenticating in the External Service"
        )
    )
    endpoint_classify = models.CharField(
        _("Endpoint for Classify"),
        max_length=100,
        default='/api/v1/classify'
    )
    endpoint_classify_dataset = models.CharField(
        _("Endpoint for Classify Dataset"),
        max_length=100,
        default='/api/v1/classify-dataset'
    )
    timeout = models.DecimalField(
        _("Request Timeout (s)"),
        max_digits=5, decimal_places=2,
        default=10,
        help_text=_("Seconds to wait for a response from the service")
    )
    metadata = models.JSONField(
        "Metadata",
        default=dict, blank=True, null=True
    )
    last_updated = models.DateTimeField(
        _("Last Updated Timestamp"),
        auto_now=True,
    )
    metrics = models.CharField(
        _("Metrics"),
        max_length=200, blank=True, null=True,
        help_text=_(
            "Metrics (sklearn) to be evaluated with the external classifier, "
            "separated by comma and space, i.e. 'accuracy_score, "
            "precision_score, recall_score, fowlkes_mallows_score'")
        )

    class Meta:
        verbose_name = _("External Classifier")
        verbose_name_plural = _("External Classifiers")

    def __str__(self):
        return self.name

    @property
    def is_inferred(self):
        return True

    def predict(self, data, include_scores=True):
        """
        TODO: Use NetworkErrorLog and authentication if available
        """
        try:
            response = self._requests_client.post(
                self.service_url + self.endpoint_classify,
                data=data,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(response.content)
        except Exception:
            raise Exception(_("Classification Service Unavailable"))

    def _get_auth_header(self):
        if self.remote_user_token:
            return {
                "Authorization": "Token {0}".format(self.remote_user_token)
            }
        else:
            return {}

    def eval_metrics(self):
        queryset = Data.objects.filter(is_finished=True)
        data = DataClassificationSerializer(queryset, many=True).data
        true_values = list(
            queryset.values_list(Data.LEARNING_LABELS, flat=True)
        )
        url = self.service_url + self.endpoint_classify_dataset
        try:
            response = self._requests_client.post(
                url, headers=self._get_auth_header(), timeout=self.timeout,
                json={"dataset": data}
            )
            if status.is_success(response.status_code):
                result = [
                    True if r == 'POSITIVE' else False
                    for r in response.json()['result']
                ]
            else:
                self.errors_log.create(
                    action=NetworkErrorLog.ACTION_CLASSIFY, url=url,
                    status_code=response.status_code, message=response.content
                )
                return False
        except Exception as e:
            self.errors_log.create(
                action=NetworkErrorLog.ACTION_CLASSIFY, url=url, message=e
            )
            return False
        metrics_scores = {}
        metrics = self._get_metrics()
        for metric in metrics:
            metrics_scores[metric] = metrics[metric](true_values, result)
        return metrics_scores

    def update_metadata(self, save=True):
        url = self.service_url + self.endpoint_classify_dataset
        try:
            response = self._requests_client.get(
                url, headers=self._get_auth_header(), timeout=self.timeout
            )
            if status.is_success(response.status_code):
                metadata = response.json()
            else:
                self.errors_log.create(
                    action=NetworkErrorLog.ACTION_OTHER, url=url,
                    status_code=response.status_code, message=response.content
                )
                return False
        except Exception as e:
            self.errors_log.create(
                    action=NetworkErrorLog.ACTION_OTHER, url=url, message=e
                )
            return False
        errors = False
        self.metadata = metadata
        local_classifier = \
            CurrentClassifier.objects.last().get_local_classifier()
        local_supported_fields = local_classifier.metadata["inference"][
            "current"]["conf"]["data_model"]["learning_fields_supported"]
        external_supported_fields = self.metadata["inference"][
            "current"]["conf"]["data_model"]["learning_fields_supported"]
        supported_fields_diff = list(
            set(local_supported_fields).symmetric_difference(
                set(external_supported_fields))
        )
        self.metadata["local_classifier"] = {
            "learning_fields_supported_diff": supported_fields_diff or "None"
        }
        self.metadata["meta"]["descriptions"][
            "learning_fields_supported_diff"] = "Supported Fields Differences"
        local_cols_na = local_classifier.metadata["inference"][
            "current"]["learning_data"]["cols_na"]
        external_cols_na = self.metadata["inference"][
            "current"]["learning_data"]["cols_na"]
        cols_na_diff = list(
            set(local_cols_na).symmetric_difference(set(external_cols_na))
        )
        self.metadata["local_data"] = {"cols_na_diff": cols_na_diff or "None"}
        self.metadata["meta"]["descriptions"]["cols_na_diff"] = \
            "Non-Available Columns differences"
        if self.metrics:
            metrics_metadata = self.eval_metrics()
            if metrics_metadata:
                self.metadata["local_data"]["scores"] = metrics_metadata
            else:
                errors = True
        self.metadata["last_updated"] = str(timezone.now())
        if save:
            self.save()
        return self.metadata if not errors else False

    def _get_metrics(self):
        if self.metrics:
            return {
                metric: getattr(sklearn_metrics, metric)
                for metric in self.metrics.split(', ')
            }
        else:
            return {}

    def clean(self):
        super().clean()
        if self.metrics:
            for metric in self.metrics.split(", "):
                if not getattr(sklearn_metrics, metric, None):
                    raise ValidationError({'metrics': _(
                        'Unrecognized metric: {}'.format(metric)
                    )})


class NetworkNode(ExternalClassifier):
    DATA_SHARING_MODE_ON_UPDATE = 0
    DATA_SHARING_MODE_ON_FINISHED = 1

    unit = models.OneToOneField(
        "units.Unit",
        on_delete=models.PROTECT,
        verbose_name=_("Unit"),
        blank=True, null=True,
        related_name='network_node'
    )
    user = models.OneToOneField(
        "base.User",
        on_delete=models.PROTECT,
        verbose_name=_("User"),
        blank=True, null=True,
        related_name='network_node'
    )
    endpoint_data = models.CharField(
        _("Endpoint for Data"),
        max_length=100,
        default='/api/v1/data'
    )
    data_sharing_is_enabled = models.BooleanField(
        _("Data Sharing - Is Enabled?"),
        default=True
    )
    data_sharing_mode = models.PositiveSmallIntegerField(
        _("Data Sharing - Mode"),
        choices=((DATA_SHARING_MODE_ON_UPDATE, _("On Update")),
                 (DATA_SHARING_MODE_ON_FINISHED, _("On Finished"))),
        default=DATA_SHARING_MODE_ON_UPDATE
    )
    classification_request = models.BooleanField(
        _("Request Classification Service"),
        default=True
    )

    class Meta:
        verbose_name = "Network Node"
        verbose_name_plural = "Network Nodes"

    def __str__(self):
        return "{}".format(self.name)

    def share_data(self, data):
        url = self.service_url + self.endpoint_data
        if isinstance(data, models.Model):
            data = DataShareSerializer(instance=data).data
        try:
            response = self._requests_client.put(
                url, data=data,
                headers=self._get_auth_header(),
                timeout=self.timeout
            )
            if status.is_success(response.status_code):
                return True
            else:
                self.errors_log.create(
                    action=NetworkErrorLog.ACTION_SHARE_DATA, url=url,
                    status_code=response.status_code, message=response.content
                )
                return False
        except Exception as e:
            self.errors_log.create(
                    action=NetworkErrorLog.ACTION_SHARE_DATA, url=url,
                    message=e
                )
            return False


class NetworkErrorLog(models.Model):
    ACTION_OTHER = 0
    ACTION_CLASSIFY = 1
    ACTION_SHARE_DATA = 2

    ACTION_CHOICES = (
        (ACTION_OTHER, _("Other")),
        (ACTION_CLASSIFY, _("Classify")),
        (ACTION_SHARE_DATA, _("Share Data"))
    )

    timestamp = models.DateTimeField(
        _("Timestamp"),
        auto_now=True
    )
    external_service = models.ForeignKey(
        "base.ExternalClassifier",
        on_delete=models.CASCADE,
        related_name="errors_log"
    )
    action = models.PositiveSmallIntegerField(
        _("Action"),
        choices=ACTION_CHOICES,
        default=ACTION_OTHER
    )
    url = models.CharField(
        _("URL"),
        max_length=200
    )
    status_code = models.PositiveSmallIntegerField(
        _("Status Code"),
        blank=True, null=True
    )
    message = models.CharField(
        _("Error Message"),
        max_length=512
    )

    class Meta:
        verbose_name = _("Network Error Log")
        verbose_name_plural = _("Network Error Logs")

    def __str__(self):
        return "{0}: {1} | {2}".format(
            self.timestamp, self.external_service, self.get_action_display()
        )


def data_saved(sender, instance, **kwargs):
    nodes = NetworkNode.objects\
        .filter(data_sharing_is_enabled=True).exclude(unit=instance.unit)
    for node in nodes:
        if node.data_sharing_mode == node.DATA_SHARING_MODE_ON_UPDATE:
            node.share_data(instance)
        else:  # node.data_sharing_mode == node.DATA_SHARING_MODE_ON_FINISHED:
            if instance.is_finished:
                node.share_data(instance)


post_save.connect(data_saved, sender='data.Data')


class CovidHTMixin:

    def _get_data_queryset(self):
        qs = super()._get_data_queryset()
        return qs.filter(is_finished=True)


class DecisionTree(CovidHTMixin, HGBTreeClassifier):
    pass


class SVM(CovidHTMixin, SVC):
    pass
