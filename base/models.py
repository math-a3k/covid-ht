#
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


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
        'supervised_learning.HGBTree',
        on_delete=models.PROTECT,
        related_name='current_classifier',
    )

    class Meta:
        verbose_name = _("Current Classifier")

    def __str__(self):
        return str(self.classifier)
