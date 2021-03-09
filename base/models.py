#
import requests

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


from django_ai.supervised_learning.models import HGBTreeClassifier, SVC


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

    def clean(self):
        if not self.classifier and not self.external:
            raise ValidationError(
                _("Both classifier and external can't be null")
            )

    class Meta:
        verbose_name = _("Current Classifier")

    def __str__(self):
        return str(self.classifier)


class ExternalClassifier(models.Model):
    _requests_client = requests

    name = models.CharField(
        _("Name"),
        max_length=100
    )
    classifier_url = models.URLField(
        _("Classifier URL"),
        default="http://localhost/api/v1/classify"
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

    class Meta:
        verbose_name = _("Extenal Classifier")
        verbose_name_plural = _("Extenal Classifiers")

    def __str__(self):
        return self.name

    @property
    def is_inferred(self):
        return True

    def predict(self, data):
        response = self._requests_client.post(
            self.classifier_url,
            data=data,
            timeout=self.timeout
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(_("Classification Service Unavailable"))


class NetworkNode(models.Model):
    DATA_SHARING_MODE_ON_UPDATE = 0
    DATA_SHARING_MODE_ON_FINISHED = 1

    name = models.CharField(
        _("Name"),
        max_length=100
    )
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
    node_url = models.URLField(
        _("Network Node's URL"),
        default="http://localhost"
    )
    endpoint_data = models.CharField(
        _("Endpoint for Data"),
        max_length=100,
        default='/api/v1/data'
    )
    endpoint_classify = models.CharField(
        _("Endpoint for Classify"),
        max_length=100,
        default='/api/v1/classify'
    )
    endpoint_classify_set = models.CharField(
        _("Endpoint for Classify Set"),
        max_length=100,
        default='/api/v1/classify_set'
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
    last_updated = models.DateTimeField(
        _("Last Updated Timestamp"),
        blank=True, null=True
    )
    metadata = models.JSONField(
        _("Metadata"),
        default=dict
    )

    class Meta:
        verbose_name = "Network Node"
        verbose_name_plural = "Network Nodes"

    def __str__(self):
        return "{}".format(self.name)


class DecisionTree(HGBTreeClassifier):
    pass


class SVM(SVC):
    pass
