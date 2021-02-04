#
import numpy as np


def trunc_normal(a, b, mean, sd, size):
    rs = np.random.normal(mean, sd, size)
    rs1 = [r if r > a else a for r in rs]
    rs2 = [r if r < b else b for r in rs1]
    return rs2
