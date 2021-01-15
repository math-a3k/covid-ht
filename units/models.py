#
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Unit(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=50
    )
    description = models.CharField(
        _("Description"),
        max_length=250
    )
    timezone = models.CharField(
        _("Time zone"),
        default="America/Lima", max_length=100
    )
    timestamp = models.DateTimeField(default=now)
    is_active = models.BooleanField(
        _("Is Active?"),
        default=True
    )
    # Possible fields:
    # Healthcare dependency
    # Geolocation
    # Address
    # City
    # State
    # Country

    class Meta:
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")

    def __str__(self):
        return self.name

    def url(self):
        return(reverse('units:detail', args=[self.pk]))
