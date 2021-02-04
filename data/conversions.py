#
from decimal import Decimal


def percentage(conversion_field_value, relative_to_value):
    return relative_to_value * conversion_field_value / 100


def mmolL_to_gL(value, other=None):
    # Needs revision
    return value * Decimal("1.62")


def umolL_to_mgdL(value, other=None):
    # Needs revision
    return value * Decimal("6.25")


def umolL_to_mgL(value, other=None):
    # Needs revision
    return value * Decimal("6.25") / Decimal("10")


def gdL_to_gL(value, other=None):
    # Needs revision
    return value / Decimal("10")


def fmolcell_to_pgcell(value, other=None):
    # Needs revision
    return value * Decimal("16.114")


def mgmL_to_kUIL(value, other=None):
    # Needs revision
    return value * Decimal("5.3")


CONVERSION_FUNCTIONS = {
    'percentage': percentage,
    'mmolL_to_gL': mmolL_to_gL,
    'umolL_to_mgdL': umolL_to_mgdL,
    'umolL_to_mgL': umolL_to_mgL,
    'fmolcell_to_pgcell': fmolcell_to_pgcell,
    'gdL_to_gL': gdL_to_gL,
    'mgmL_to_kUIL': mgmL_to_kUIL
}


def unit_conversion(value, from_unit, to_unit, relative_to_value=None):
    if from_unit == 'percentage':
        conv_function = 'percentage'
    else:
        conv_function = "{0}_to_{1}".format(from_unit, to_unit)
    return CONVERSION_FUNCTIONS[conv_function](value, relative_to_value)
