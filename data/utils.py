#
import numpy as np


def trunc_normal(a, b, mean, sd, size):
    rs = np.random.normal(mean, sd, size)
    rs1 = [r if r > a else a for r in rs]
    rs2 = [r if r < b else b for r in rs1]
    return rs2


def percentage(conversion_field_value, relative_to_value):
    return relative_to_value * conversion_field_value / 100


CONVERSION_FUNCTIONS = {
    'percentage': percentage,
}
