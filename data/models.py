import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinValueValidator, )
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .conversions import unit_conversion


class ConversionFieldsModelMixin:

    @classmethod
    def get_conversion_fields(cls):
        return [
            field.attname for field in Data._meta.get_fields()
            if "_U" in field.attname
        ]

    def parse_field_name(self, field_name):
        main_field, conv_rule = field_name.split('_U')
        if "R" in conv_rule:
            unit, relative_to_field = conv_rule.split('_R')
        else:
            unit, relative_to_field = (conv_rule, None)
        return (main_field, unit, relative_to_field)

    def get_conversion_fields_for_field(self, field):  # pragma: no cover
        return [
            f.attname for f in self._meta.get_fields()
            if f.attname.startswith(field + "_U")
        ]

    def get_converted_field_value(self, field):  # pragma: no cover
        conversion_fields = self.get_conversion_fields_for_field(field)
        for c_field in conversion_fields:
            if getattr(self, c_field, None):
                return self.get_conversion_value(c_field)
        return None

    def get_conversion_value(self, conversion_field):
        conversion_field_value = getattr(self, conversion_field, None)
        if not conversion_field_value:
            return None
        main_field, from_unit, relative_to_field = \
            self.parse_field_name(conversion_field)
        to_unit = self.MAIN_FIELDS_UNITS[main_field]['unit']
        if relative_to_field:
            relative_to_value = getattr(self, relative_to_field, None)
            # Not used yet - for the future
            if not relative_to_value:  # pragma: no cover
                relative_to_value = \
                    self.get_converted_field_value(relative_to_field)
        else:
            relative_to_value = None
        #
        return unit_conversion(
            conversion_field_value, from_unit, to_unit, relative_to_value
        )

    def apply_conversion_fields_rules(self):
        applied = []
        fields = [f.attname for f in self._meta.get_fields()]
        for field in fields:
            if 'U' in field:
                converted_value = self.get_conversion_value(field)
                if converted_value:
                    main_field, from_unit, relative_to_field = \
                        self.parse_field_name(field)
                    setattr(
                        self, main_field, converted_value
                    )
                    applied.append(field)
        return applied

    def clean(self):
        for conversion_field in self.get_conversion_fields():
            if getattr(self, conversion_field, None):
                main_field, from_unit, relative_to_field = \
                    self.parse_field_name(conversion_field)
                if relative_to_field and \
                        not getattr(self, relative_to_field, None):
                    raise ValidationError(
                        {relative_to_field:
                            _('This field must be present in order to use '
                              '%(field)s' % {'field': conversion_field})}
                    )

    def save(self, *args, **kwargs):
        self.clean()
        self.apply_conversion_fields_rules()
        super().save(*args, **kwargs)


class Data(ConversionFieldsModelMixin, models.Model):
    """
    Main Data object - Hemogram result fields, auxiliary variables fields
    and input related fields
    """
    HEMOGRAM_MAIN_FIELDS = {
        'rbc': {'unit': 'x1012L', },
        'wbc': {'unit': 'x109L', },
        'hgb': {'unit': 'gL', },
        'hgbp': {'unit': 'mgdL', },
        'hgbg': {'unit': 'percentage', },
        'htg': {'unit': 'gL', },
        'hct': {'unit': 'gL', },
        'mcv': {'unit': 'fL', },
        'mch': {'unit': 'pgcell', },
        'mchc': {'unit': 'gL', },
        'rdw': {'unit': 'percentage', },
        'rtc': {'unit': 'x109L', },
        'plt': {'unit': 'x109L', },
        'mpv': {'unit': 'fL', },
        'pt': {'unit': 's', },
        'inr': {'unit': None, },
        'aptt': {'unit': 's', },
        'tct': {'unit': 's', },
        'fbg': {'unit': 'gL', },
        'atb': {'unit': 'kUIL', },
        'bt': {'unit': 'minutes', },
        'vsy': {'unit': 'cP', },
        'esr': {'unit': 'mmH', },
        'crp': {'unit': 'mgL', },
        'aat': {'unit': 'mgL', },
        'pct': {'unit': 'mgL', },
        'neut': {'unit': 'x109L'},
        'nbf': {'unit': 'x109L'},
        'lymp': {'unit': 'x109L'},
        'mono': {'unit': 'x109L'},
        'mnl': {'unit': 'x109L'},
        'cd4': {'unit': 'x109L'},
        'eo': {'unit': 'x109L'},
        'baso': {'unit': 'x109L'},
        'iga': {'unit': 'x109L'},
        'igd': {'unit': 'x109L'},
        'ige': {'unit': 'x109L'},
        'igg': {'unit': 'x109L'},
        'igm': {'unit': 'x109L'}
    }
    MAIN_FIELDS_UNITS = HEMOGRAM_MAIN_FIELDS

    AUXILIARY_FIELDS = [
        'age', 'sex', 'is_diabetic', 'is_hypertense', 'is_overweight',
        'is_at_altitude', 'is_with_other_conds',
    ]
    CHTUID_FIELD = ['chtuid'] if settings.CHTUID_USE_IN_CLASSIFICATION else []

    LEARNING_FIELDS_CATEGORICAL = CHTUID_FIELD + [
        'sex', 'is_diabetic', 'is_hypertense', 'is_overweight',
        'is_at_altitude', 'is_with_other_conds',
    ]
    LEARNING_LABELS = 'is_covid19'
    LEARNING_FIELDS_MONOTONIC_CONSTRAINTS = "None"
    # conversion_function = unit_conversion

    SEX_CHOICES = (
        (None, _("Not Available")),
        (False, _("Female")),
        (True, _("Male"))
    )

    # METADATA FIELDS
    chtuid = models.CharField(
        _("Covid-HT Unique IDentifier"),
        max_length=5, blank=True,
        default=settings.CHTUID
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
    is_finished = models.BooleanField(
        _("Is Finished?"),
        default=False,
        help_text=_(
            'Is the record finished or complete? All data has been recorded '
            'and the internal identifier has been removed.'
        )
    )
    unit_ii = models.CharField(
        _("Unit Internal Identifier"),
        max_length=50,
        blank=True, null=True,
        help_text=_('Unit Internal Identifier for mapping to physical record'),
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True
    )
    timestamp = models.DateTimeField(
        _("Timestamp"),
        default=now
    )
    # -> CLASSIFICATION FIELDS
    # LABELS
    is_covid19 = models.BooleanField(
        _("Is COVID19?"),
        blank=True, null=True
    )
    # AUXILIARY FIELDS
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
    # HEMOGRAM FIELDS
    # Red Blood Cells
    rbc = models.DecimalField(
        _("RBC (x10^12/L)"),
        max_digits=5, decimal_places=3,
        blank=True, null=True,
        help_text=_('Red Blood Cells (x10^12/L or mlm/mm^3)'),
        validators=[MinValueValidator(2.0), MaxValueValidator(8.0)]
    )
    hgb = models.SmallIntegerField(
        _("HGB (g/L)"),
        blank=True, null=True,
        help_text=_('Hemoglobin (g/L)'),
        validators=[MinValueValidator(50), MaxValueValidator(250)]
    )
    hgb_UmmolL = models.DecimalField(
        _("HGB (mmol/L)"),
        max_digits=4, decimal_places=3,
        blank=True, null=True,
        help_text=_('Hemoglobin (mmol/L)'),
        validators=[MinValueValidator(0.5), MaxValueValidator(4)]
    )
    hgbp = models.SmallIntegerField(
        _("HGBP (mg/dL)"),
        blank=True, null=True,
        help_text=_('Hemoglobin in Plasma (mg/dL)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(8)]
    )
    hgbp_UumolL = models.DecimalField(
        _("HGBP (umol/L)"),
        max_digits=3, decimal_places=2,
        blank=True, null=True,
        help_text=_('Hemoglobin in Plasma (umol/L)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(2)]
    )
    hgbg = models.DecimalField(
        _("Glycated Hemoglobin (% of HGB)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Glycated Hemoglobin (% of Hemoglobin)'),
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    htg = models.DecimalField(
        _("HTG (g/L)"),
        max_digits=4, decimal_places=3,
        blank=True, null=True,
        help_text=_('Haptoglobin (g/L)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(5)]
    )
    hct = models.DecimalField(
        _("HCT (L/L)"),
        max_digits=3, decimal_places=2,
        blank=True, null=True,
        help_text=_('Hematocrit (g/L)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(1)]
    )
    mcv = models.SmallIntegerField(
        _("MCV (fL)"),
        blank=True, null=True,
        help_text=_('Mean Cell Volume (fL)'),
        validators=[MinValueValidator(50), MaxValueValidator(150)]
    )
    mch = models.SmallIntegerField(
        _("MCH (pg/cell)"),
        blank=True, null=True,
        help_text=_('Mean Cell Hemoglobin (pg/cell)'),
        validators=[MinValueValidator(10), MaxValueValidator(50)]
    )
    mch_Ufmolcell = models.SmallIntegerField(
        _("MCH (fmol/cell)"),
        blank=True, null=True,
        help_text=_('Mean Cell Hemoglobin (fmol/cell)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(2)]
    )
    mchc = models.SmallIntegerField(
        _("MCHC (g/L)"),
        blank=True, null=True,
        help_text=_('Mean Corpuscular Hemoglobin Concentration (g/L)'),
        validators=[MinValueValidator(2), MaxValueValidator(5)]
    )
    mchc_UgdL = models.SmallIntegerField(
        _("MCHC (g/dL)"),
        blank=True, null=True,
        help_text=_('Mean Corpuscular Hemoglobin Concentration (g/dL)'),
        validators=[MinValueValidator(20), MaxValueValidator(50)]
    )
    mchc_UmmolL = models.SmallIntegerField(
        _("MCHC (mmol/L)"),
        blank=True, null=True,
        help_text=_('Mean Corpuscular Hemoglobin Concentration (mmol/L)'),
        validators=[MinValueValidator(2), MaxValueValidator(8)]
    )
    rdw = models.DecimalField(
        _("RDW (%)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Red Blood Cell Distribution Width (%)'),
        validators=[MinValueValidator(5.0), MaxValueValidator(30.0)]
    )
    rtc = models.DecimalField(
        _("Reticulocytes (x10^9/L)"),
        blank=True, null=True,
        max_digits=4, decimal_places=2,
        help_text=_('Reticulocytes (x10^9/L)'),
        validators=[MinValueValidator(5.0), MaxValueValidator(250.0)]
    )
    rtc_Upercentage_Rrbc = models.DecimalField(
        _("RTC (% of RBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Reticulocytes (% of RBC)'),
        validators=[MinValueValidator(0), MaxValueValidator(50.0)]
    )
    # Coagulation
    plt = models.SmallIntegerField(
        _("PLT (x10^9/L)"),
        blank=True, null=True,
        help_text=_('Platelets (x10^9/L or x1000/uL)'),
        validators=[MinValueValidator(50), MaxValueValidator(1000)]
    )
    mpv = models.DecimalField(
        _("MPV (fL)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Mean Platelet Volume (fL)'),
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    pt = models.DecimalField(
        _("PT (s)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Prothrombin Time (s)'),
        validators=[MinValueValidator(50), MaxValueValidator(550)]
    )
    inr = models.DecimalField(
        _("INR"),
        max_digits=3, decimal_places=2,
        blank=True, null=True,
        help_text=_('International Normalized Ratio'),
        validators=[MinValueValidator(0.1), MaxValueValidator(3)]
    )
    aptt = models.SmallIntegerField(
        _("APTT (s)"),
        blank=True, null=True,
        help_text=_('Activated Partial Thromboplastin Time (s)'),
        validators=[MinValueValidator(5), MaxValueValidator(120)]
    )
    tct = models.SmallIntegerField(
        _("TCT (s)"),
        blank=True, null=True,
        help_text=_('Activated Partial Thromboplastin Time (s)'),
        validators=[MinValueValidator(5), MaxValueValidator(50)]
    )
    fbg = models.DecimalField(
        _("FBG (g/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Fibrogen (g/L)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(9)]
    )
    atb = models.DecimalField(
        _("ATB (kIU/L)"),
        max_digits=3, decimal_places=2,
        blank=True, null=True,
        help_text=_('Antithrombin (kIU/L)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(4)]
    )
    atb_UmgmL = models.DecimalField(
        _("ATB (mg/mL)"),
        max_digits=3, decimal_places=2,
        blank=True, null=True,
        help_text=_('Antithrombin (mg/mL)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(2)]
    )
    bt = models.DecimalField(
        _("BT (minutes)"),
        max_digits=3, decimal_places=2,
        blank=True, null=True,
        help_text=_('Bleeding Time (minutes)'),
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    vsy = models.DecimalField(
        _("VSY (cP)"),
        max_digits=3, decimal_places=2,
        blank=True, null=True,
        help_text=_('Viscosity (cP)'),
        validators=[MinValueValidator(0.1), MaxValueValidator(4)]
    )
    # White Blood Cells
    wbc = models.DecimalField(
        _("WBC (x10^9/L)"),
        max_digits=5, decimal_places=3,
        blank=True, null=True,
        help_text=_(
            'White Blood Cells (x10^12/L or x10^3/mm^3 or x10^3/uL^3)'
        ),
        validators=[MinValueValidator(1.0), MaxValueValidator(50.0)]
    )
    neut = models.DecimalField(
        _("NEUT (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Neutrophil Granulocytes (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(30.0)]
    )
    neut_Upercentage_Rwbc = models.DecimalField(
        _("NEUT (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Neutrophil Granulocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(99.0)]
    )
    nbf = models.DecimalField(
        _("NBF (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Neutrophilic Band Forms (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(2)]
    )
    nbf_Upercentage_Rwbc = models.DecimalField(
        _("NBF (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Neutrophilic Band Forms (% of White Blood Cells)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(99.0)]
    )
    lymp = models.DecimalField(
        _("LYMPH (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Lymphocytes (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(30.0)]
    )
    lymp_Upercentage_Rwbc = models.DecimalField(
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
        validators=[MinValueValidator(0.01), MaxValueValidator(30.0)]
    )
    mono_Upercentage_Rwbc = models.DecimalField(
        _("MONO (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Monocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(99.0)]
    )
    mnl = models.DecimalField(
        _("MNL (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Mononuclear Leukocytes (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(20.0)]
    )
    mnl_Upercentage_Rwbc = models.DecimalField(
        _("MNL (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Mononuclear Leukocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(99.0)]
    )
    cd4 = models.DecimalField(
        _("CD4 (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('CD4+ T cells (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    eo = models.DecimalField(
        _("EO (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Eosinophils (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    eo_Upercentage_Rwbc = models.DecimalField(
        _("EO (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Eosinophil Granulocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.0)]
    )
    baso = models.DecimalField(
        _("BASO (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Basophil Granulocytes (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    baso_Upercentage_Rwbc = models.DecimalField(
        _("BASO (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Basophil Granulocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(99.0)]
    )
    iga = models.DecimalField(
        _("IGA (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Inmunoglobulines A (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(1000.0)]
    )
    # Inmunoglubulines
    igd = models.DecimalField(
        _("IGD (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Inmunoglobulines D (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    ige = models.DecimalField(
        _("IGE (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Inmunoglobulines E (x10^9/L)'),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    igg = models.DecimalField(
        _("IGG (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Inmunoglobulines G (x10^9/L)'),
        validators=[MinValueValidator(100.0), MaxValueValidator(2500.0)]
    )
    igm = models.DecimalField(
        _("IGM (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Inmunoglobulines - M (x10^9/L)'),
        validators=[MinValueValidator(10.0), MaxValueValidator(400.0)]
    )
    # Acute Phase Proteins
    esr = models.SmallIntegerField(
        _("ESR (mm/H)"),
        blank=True, null=True,
        help_text=_('Erythrocyte Sedimentation Rate (mm/H)'),
        validators=[MinValueValidator(0), MaxValueValidator(200)]
    )
    crp = models.SmallIntegerField(
        _("CRP (mg/L)"),
        blank=True, null=True,
        help_text=_('C Reactive Protein (mg/L)'),
        validators=[MinValueValidator(0), MaxValueValidator(15)]
    )
    crp_UnmolL = models.SmallIntegerField(
        _("CRP (nmol/L)"),
        blank=True, null=True,
        help_text=_('C Reactive Protein (nmol/L)'),
        validators=[MinValueValidator(0), MaxValueValidator(500)]
    )
    aat = models.SmallIntegerField(
        _("AAT (mg/L)"),
        blank=True, null=True,
        help_text=_('Alpha 1-antitrypsin (mg/dL)'),
        validators=[MinValueValidator(50), MaxValueValidator(500)]
    )
    aat_UumolL = models.SmallIntegerField(
        _("AAT (umol/L)"),
        blank=True, null=True,
        help_text=_('Alpha 1-antitrypsin (umol/L)'),
        validators=[MinValueValidator(5), MaxValueValidator(150)]
    )
    pct = models.DecimalField(
        _("PCT (ng/dL)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Procalcitonin (ng/dL or ug/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(2.0)]
    )

    class Meta:
        verbose_name = _("Data")
        verbose_name_plural = _("Data")
        ordering = ['-timestamp']

    def __str__(self):
        return "{0}: {1}".format(self.uuid, self.is_covid19)

    def url(self):
        return(reverse('data:detail', args=[self.uuid]))

    def clean(self):
        super().clean()
        if self.is_finished and \
                getattr(self, self.LEARNING_LABELS, None) is None:
            raise ValidationError(
                {self.LEARNING_LABELS:
                    _('A record can not be marked as finished when the label'
                      ' is not present.')}
            )

    @classmethod
    def get_hemogram_main_fields(cls):
        return [field for field in Data.HEMOGRAM_MAIN_FIELDS]

    @classmethod
    def _get_learning_fields(cls):
        return cls.CHTUID_FIELD + cls.AUXILIARY_FIELDS \
            + cls.get_hemogram_main_fields()
