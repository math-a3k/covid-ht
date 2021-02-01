#
import uuid

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.validators import (MaxValueValidator, MinValueValidator, )
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .utils import CONVERSION_FUNCTIONS


class Data(models.Model):
    """
    Main Data object - Hemogram result fields, auxiliary variables fields
    and input related fields
    """
    HEMOGRAM_FIELDS = [
        'rbc', 'wbc', 'hgb', 'hct', 'mcv', 'mch', 'mchc', 'rdw', 'plt', 'neut',
        'lymp', 'mono', 'eo', 'baso', 'iga', 'igm',
    ]
    CONVERSION_FIELDS = [
        'neut_percentage', 'lymp_percentage', 'mono_percentage',
        'eo_percentage', 'baso_percentage',
    ]
    CONVERSION_FIELDS_RULES = {
        'neut_percentage': {
            'main_field': 'neut',
            'conversion': 'percentage',
            'relative_to': 'wbc',
        },
        'lymp_percentage': {
            'main_field': 'lymp',
            'conversion': 'percentage',
            'relative_to': 'wbc',
        },
        'mono_percentage': {
            'main_field': 'mono',
            'conversion': 'percentage',
            'relative_to': 'wbc',
        },
        'eo_percentage': {
            'main_field': 'eo',
            'conversion': 'percentage',
            'relative_to': 'wbc',
        },
        'baso_percentage': {
            'main_field': 'baso',
            'conversion': 'percentage',
            'relative_to': 'wbc',
        },
    }

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
    # HEMOGRAM RESULTS FIELDS
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
    neut_percentage = models.DecimalField(
        _("NEUT (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Neutrophils (% of White Blood Cells)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(99.0)]
    )
    lymp = models.DecimalField(
        _("LYMPH (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Lymphocytes (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(30.0)]
    )
    lymp_percentage = models.DecimalField(
        _("LYMPH (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Lymphocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(99.0)]
    )
    mono = models.DecimalField(
        _("MONO (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Monocytes (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(15.0)]
    )
    mono_percentage = models.DecimalField(
        _("MONO (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Monocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(99.0)]
    )
    eo = models.DecimalField(
        _("EO (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Eosinophils (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    eo_percentage = models.DecimalField(
        _("EO (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Eosinophils (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.0)]
    )
    baso = models.DecimalField(
        _("BASO (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Basophils (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    baso_percentage = models.DecimalField(
        _("BASO (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Basophils (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.0)]
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
        return(reverse('data:detail', args=[self.uuid]))

    def get_conversion_fields(self, field):  # pragma: no cover
        c_fields = []
        for conv_field in self.CONVERSION_FIELDS_RULES:
            if self.CONVERSION_FIELDS_RULES[conv_field]['main_field'] == field:
                c_fields.append(conv_field)
        return c_fields

    def get_converted_field_value(self, field):  # pragma: no cover
        conversion_fields = self.get_conversion_fields(field)
        for c_field in conversion_fields:
            if getattr(self, c_field, None):
                return self.get_conversion_value(c_field)
        return None

    def get_conversion_value(self, conversion_field):
        conversion_field_value = getattr(self, conversion_field, None)
        if not conversion_field_value:
            return None
        conv_rule = self.CONVERSION_FIELDS_RULES[conversion_field]
        conv_function = CONVERSION_FUNCTIONS.get(conv_rule.get('conversion'))
        relative_to = conv_rule.get('relative_to', None)
        relative_to_value = getattr(self, relative_to, None)
        # Not used yet - for the future
        if not relative_to_value:   # pragma: no cover
            relative_to_value = self.get_converted_field_value(relative_to)
        #
        return conv_function(conversion_field_value, relative_to_value)

    def apply_conversion_fields_rules(self):
        applied = []
        for conv_field in self.CONVERSION_FIELDS_RULES:
            converted_value = self.get_conversion_value(conv_field)
            if converted_value:
                main_field = \
                    self.CONVERSION_FIELDS_RULES[conv_field]['main_field']
                setattr(
                    self, main_field, converted_value
                )
                applied.append(conv_field)
        return applied

    def clean(self):
        for conversion_field in self.CONVERSION_FIELDS_RULES:
            if getattr(self, conversion_field, None):
                rule = self.CONVERSION_FIELDS_RULES[conversion_field]
                relative_to = rule.get('relative_to', None)
                if relative_to and not getattr(self, relative_to, None):
                    raise ValidationError(
                        {relative_to:
                            _('This field must be present in order to use '
                              '%(field)s' % {'field': conversion_field})}
                    )

    def save(self, *args, **kwargs):
        self.clean()
        self.apply_conversion_fields_rules()
        super().save(*args, **kwargs)
