from copy import copy

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .conversions import unit_conversion


class ConversionFieldsModelMixin:

    @classmethod
    def get_conversion_fields(cls):
        return [
            field.attname for field in cls._meta.get_fields()
            if "_U" in field.attname
        ]

    @classmethod
    def parse_field_name(cls, field_name):
        main_field, conv_rule = field_name.split('_U')
        if "R" in conv_rule:
            unit, relative_to_field = conv_rule.split('_R')
        else:
            unit, relative_to_field = (conv_rule, None)
        return (main_field, unit, relative_to_field)

    @classmethod
    def get_conversion_value(cls, conversion_field, obj):
        if not isinstance(obj, dict):
            conversion_field_value = getattr(obj, conversion_field, None)
        else:
            conversion_field_value = obj.get(conversion_field, None)
        if not conversion_field_value:
            return None
        main_field, from_unit, relative_to_field = \
            cls.parse_field_name(conversion_field)
        to_unit = cls.MAIN_FIELDS_UNITS[main_field]['unit']
        if relative_to_field:
            if not isinstance(obj, dict):
                relative_to_value = getattr(obj, relative_to_field, None)
            else:
                relative_to_value = obj.get(relative_to_field, None)
        else:
            relative_to_value = None
        #
        return unit_conversion(
            conversion_field_value, from_unit, to_unit, relative_to_value
        )

    @classmethod
    def apply_conversion_fields_rules_to_dict(cls, dict_obj):
        _dict = copy(dict_obj)
        # TBI:
        # 'dictionary changed size during iteration' runtime error is
        # triggered if dict_obj is not copied and data is submitted with
        # 'app/json' (and in tests) while it doesn't when submitted
        # with 'multipart/form-data' - how it gets circumvented?
        for field in dict_obj:
            if 'U' in field:
                conversion_value = cls.get_conversion_value(field, dict_obj)
                if conversion_value:
                    main_field, from_unit, relative_to_field = \
                        cls.parse_field_name(field)
                    _dict[main_field] = conversion_value
        return _dict

    def apply_conversion_fields_rules(self):
        applied = []
        fields = [f.attname for f in self._meta.get_fields()]
        for field in fields:
            if 'U' in field:
                conversion_value = self.get_conversion_value(field, self)
                if conversion_value:
                    main_field, from_unit, relative_to_field = \
                        self.parse_field_name(field)
                    setattr(self, main_field, conversion_value)
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
