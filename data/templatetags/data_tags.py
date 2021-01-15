#
from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag
def get_row_field(row, field):
    """
    Returns the field of a row
    """
    if field.choices:
        value = getattr(row, "get_{0}_display".format(field.attname))()
    elif hasattr(field, 'get_internal_type'):
        if "Date" in getattr(field, 'get_internal_type')():
            value = getattr(row, field.attname).strftime("%Y-%m-%d %H:%M")
        else:
            value = getattr(row, field.attname)
    else:
        value = getattr(row, field.attname)
    if value is None:
        return "Not Available"
    else:
        if isinstance(value, bool):
            return _("Yes") if value else _("No")
        else:
            return value
