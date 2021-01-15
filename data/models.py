#
import uuid

from django.core.validators import (MaxValueValidator, MinValueValidator, )
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Data(models.Model):
    SEX_CHOICES = (
        (None, _("Not Available")),
        (False, _("Female")),
        (True, _("Male"))
    )
    unit = models.ForeignKey(
        "units.Unit",
        on_delete=models.PROTECT,
        verbose_name=_("Unit"),
        related_name='data'
    )
    user = models.ForeignKey(
        "base.User",
        on_delete=models.PROTECT,
        verbose_name=_("User"),
        related_name='data'
    )
    unit_ii = models.CharField(
        _("Unit Internal Identifier"),
        max_length=50,
        blank=True, null=True,
        help_text=_('Unit Internal Identifier for mapping to physical record'),
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )
    timestamp = models.DateTimeField(
        _("Timestamp"),
        default=now
    )
    is_covid19 = models.BooleanField(
        _("Is COVID19?")
    )
    age = models.PositiveSmallIntegerField(
        _("Age"),
        blank=True, null=True
    )
    sex = models.BooleanField(
        _("Sex"),
        choices=SEX_CHOICES,
        blank=True, null=True
    )
    is_diabetic = models.BooleanField(
        _("Is Diabetic?"),
        null=True
    )
    is_hypertense = models.BooleanField(
        _("Is Hypertense?"),
        null=True
    )
    is_overweight = models.BooleanField(
        _("Is Overweight Patient?"),
        null=True
    )
    is_at_altitude = models.BooleanField(
        _("Is at Altitude?"),
        null=True,
        help_text=_('Is the Patient at High Altitude (> 1500m)'),
    )
    is_with_other_conds = models.BooleanField(
        _("Is with other Relevant Conditions?"),
        null=True,
        help_text=_('Is the Patient with other Relevant Conditions? '
                    '(Transplantation, Blood disorders, etc.)'),
    )
    rbc = models.DecimalField(
        _("RBC (x10^12/L)"),
        max_digits=5, decimal_places=3,
        blank=True, null=True,
        help_text=_('Red Blood Cells (x10^12/L)'),
        validators=[MinValueValidator(2.0), MaxValueValidator(8.0)]
    )
    wbc = models.DecimalField(
        _("WBC (x10^9/L)"),
        max_digits=5, decimal_places=3,
        blank=True, null=True,
        help_text=_('White Blood Cells (x10^12/L)'),
        validators=[MinValueValidator(2.0), MaxValueValidator(40.0)]
    )
    hgb = models.SmallIntegerField(
        _("HGB (g/L)"),
        blank=True, null=True,
        help_text=_('Hemoglobin (g/L)'),
        validators=[MinValueValidator(80), MaxValueValidator(240)]
    )
    hct = models.DecimalField(
        _("HCT (L/L)"),
        blank=True, null=True,
        max_digits=3, decimal_places=2,
        help_text=_('Hematocrit (g/L)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(0.9)]
    )
    mcv = models.SmallIntegerField(
        _("MCV (fL)"),
        blank=True, null=True,
        help_text=_('Mean Cell Volume (fL)'),
        validators=[MinValueValidator(60), MaxValueValidator(150)]
    )
    mch = models.SmallIntegerField(
        _("MCH (pg)"),
        blank=True, null=True,
        help_text=_('Mean Corpuscular Hemoglobin (pg)'),
        validators=[MinValueValidator(60), MaxValueValidator(150)]
    )
    mchc = models.SmallIntegerField(
        _("MCHC (g/L)"),
        blank=True, null=True,
        help_text=_('Mean Corpuscular Hemoglobin Concentration (g/L)'),
        validators=[MinValueValidator(280), MaxValueValidator(380)]
    )
    rdw = models.DecimalField(
        _("RDW (%)"),
        blank=True, null=True,
        max_digits=4, decimal_places=2,
        help_text=_('Red Blood Cell Distribution Width (%)'),
        validators=[MinValueValidator(5.0), MaxValueValidator(40.0)]
    )
    plt = models.SmallIntegerField(
        _("PLT (x10^9/L)"),
        blank=True, null=True,
        help_text=_('Platelets (x10^9/L)'),
        validators=[MinValueValidator(50), MaxValueValidator(550)]
    )
    neut = models.DecimalField(
        _("NEUT (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Neutrophils (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(40.0)]
    )
    lymp = models.DecimalField(
        _("LYMPH (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Lymphocytes (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(30.0)]
    )
    mono = models.DecimalField(
        _("MONO (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Monocytes (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(15.0)]
    )
    eo = models.DecimalField(
        _("EO (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Eosinophils (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    baso = models.DecimalField(
        _("BASO (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Basophils (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    iga = models.DecimalField(
        _("IGA (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Inmunoglobulines - Active (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    igm = models.DecimalField(
        _("IGM (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Inmunoglobulines - Memory (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )

    class Meta:
        verbose_name = _("Data")
        verbose_name_plural = _("Data")
        ordering = ['-timestamp']

    def __str__(self):
        return "{0}: {1}".format(self.uuid, self.is_covid19)

    def url(self):
        return(reverse('data:detail', args=[self.pk]))
