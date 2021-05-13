import numpy as np

np.random.seed(123456)


def trunc_normal(a, b, mean, sd, size):
    rs = np.random.normal(mean, sd, size)
    rs1 = [r if r > a else a for r in rs]
    rs2 = [r if r < b else b for r in rs1]
    return rs2


def get_hemogram_data(for_input=False, is_finished=False):
    data = {}
    is_covid19 = bool(np.random.binomial(1, 0.6, 1)[0])
    if for_input:
        data["is_covid19"] = is_covid19
        data["is_finished"] = is_finished
    #
    # Sex is ~ 55% F (0) / 45% M (1)
    data["sex"] = bool(np.random.binomial(1, 0.55, 1)[0])
    # Age is around 50, mostly between 45 and 55
    data["age"] = round(np.random.normal(50, 2, size=(1,))[0])
    data["is_diabetic"] = bool(np.random.binomial(1, 0.20, 1)[0])
    # Is Hypertense is ~ 60% F (0) / 40% T (1)
    data["is_hypertense"] = bool(np.random.binomial(1, 0.35, 1)[0])
    # Is Overweight is ~ 70% F (0) / 30% T (1)
    data["is_overweight"] = bool(np.random.binomial(1, 0.30, 1)[0])
    # Is at Altitude is ~ 70% F (0) / 30% T (1)
    data["is_at_altitude"] = bool(np.random.binomial(1, 0.30, 1)[0])
    # Is with other conds is ~ 95% F (0) / 5% T (1)
    data["is_with_other_conds"] = bool(np.random.binomial(1, 0.05, 1)[0])
    #
    data["hgb"] = round(trunc_normal(80, 240, 140, 5, 1)[0])
    data["mcv"] = round(trunc_normal(60, 150, 80, 10, 1)[0])
    data["rdw"] = round(trunc_normal(5, 40, 12, 4, 1)[0], 2)
    data["mono"] = round(trunc_normal(0.01, 15, 8, 2, 1)[0], 2)
    data["baso"] = round(trunc_normal(0.0, 10, 4, 2, 1)[0], 2)
    data["iga"] = round(trunc_normal(0.0, 10, 4, 2, 1)[0], 2)
    data["mchc"] = round(trunc_normal(2, 5, 3, 1, 1)[0])
    data["eo"] = round(trunc_normal(0, 10, 5, 2, 1)[0], 2)
    data["igm"] = round(trunc_normal(10, 400, 50, 5, 1)[0], 2)
    data["hct"] = round(trunc_normal(0.2, 0.8, 0.4, 0.2, 1)[0], 2)
    # -> Group differences
    data["rbc"] = round(trunc_normal(2, 8, 4.5, 2, 1)[0]
                        if is_covid19 else
                        trunc_normal(2, 8, 4.05, 2, 1)[0], 2)
    #
    data["wbc"] = round(trunc_normal(2, 40, 7, 4, 1)[0]
                        if is_covid19 else
                        trunc_normal(2, 40, 7.7, 5, 1)[0], 2)
    #
    data["plt"] = round(trunc_normal(50, 550, 220, 10, 1)[0]
                        if is_covid19 else
                        trunc_normal(50, 550, 242, 20, 1)[0])
    #
    data["lymp"] = round(trunc_normal(0.1, 30, 8, 1, 1)[0]
                         if is_covid19 else
                         trunc_normal(0.1, 30, 8, 4, 1)[0], 2)
    #
    data["neut"] = round(trunc_normal(0.2, 40, 5, 2, 1)[0]
                         if is_covid19 else
                         trunc_normal(0.2, 40, 5.5, 2, 1)[0], 2)

    return data
