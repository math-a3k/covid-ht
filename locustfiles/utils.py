import numpy as np

from data.utils import trunc_normal

np.random.seed(123456)


def get_hemogram_data(for_input=False):
    data = {}
    is_covid19 = bool(np.random.binomial(1, 0.6, 1)[0])
    if for_input:
        data["is_covid19"] = is_covid19
        data["is_finished"] = False
    #
    data["sex"] = bool(np.random.binomial(1, 0.55, 1)[0])
    data["age"] = int(np.floor(np.random.normal(50, 2, size=(1,)))[0])
    data["is_at_altitude"] = bool(np.random.binomial(1, 0.30, 1)[0])
    data["is_with_other_conds"] = bool(np.random.binomial(1, 0.05, 1)[0])
    #
    data["rbc"] = round(trunc_normal(2, 8, 4.5, 2, 1)[0]
                        if is_covid19 else
                        trunc_normal(2, 8, 4.3, 2, 1)[0], 2)
    data["wbc"] = round(trunc_normal(2, 40, 7, 4, 1)[0]
                        if is_covid19 else
                        trunc_normal(2, 40, 10, 5, 1)[0], 2)
    data["hgb"] = round((trunc_normal(80, 240, 140, 5, 1)[0]
                        if is_covid19 else
                        trunc_normal(80, 240, 140, 5, 1)[0]))
    data["mcv"] = round(trunc_normal(60, 150, 80, 10, 1)[0]
                        if is_covid19 else
                        trunc_normal(60, 150, 80, 10, 1)[0])
    data["rdw"] = round(trunc_normal(5, 40, 12, 4, 1)[0]
                        if is_covid19 else
                        trunc_normal(5, 40, 12, 4, 1)[0], 2)
    data["plt"] = round(trunc_normal(50, 550, 220, 17, 1)[0]
                        if is_covid19 else
                        trunc_normal(50, 550, 250, 20, 1)[0])
    data["mono"] = round(trunc_normal(0.01, 15, 8, 2, 1)[0]
                         if is_covid19 else
                         trunc_normal(0.01, 15, 8, 2, 1)[0], 2)
    data["baso"] = round(trunc_normal(0.0, 10, 4, 2, 1)[0]
                         if is_covid19 else
                         trunc_normal(0.0, 10, 4, 2, 1)[0], 2)
    data["iga"] = round(trunc_normal(0.0, 10, 4, 2, 1)[0]
                        if is_covid19 else
                        trunc_normal(0.0, 10, 4, 2, 1)[0], 2)

    data["mchc"] = round(trunc_normal(2, 5, 3, 1, 1)[0])
    data["eo"] = round(trunc_normal(0, 10, 5, 2, 1)[0], 2)
    data["igm"] = round(trunc_normal(10, 400, 50, 5, 1)[0], 2)
    data["hct"] = round(trunc_normal(0.2, 0.8, 0.4, 0.2, 1)[0], 2)
    data["lymp"] = round(trunc_normal(0.1, 30, 8, 2, 1)[0]
                         if is_covid19 else
                         trunc_normal(0.1, 30, 5, 2, 1)[0], 2)
    data["neut"] = round(trunc_normal(0.2, 40, 5, 2, 1)[0]
                         if is_covid19 else
                         trunc_normal(0.2, 40, 8, 2, 1)[0], 2)
    return data


class LoginTaskSetMixin:

    def login(self):
        response = self.client.get(self.login_url)
        self.csrf_token = response.cookies['csrftoken']
        self.client.post(
            "/accounts/login/",
            {"username": self.user_username, "password": self.user_password},
            headers={"X-CSRFToken": self.csrf_token}
        )
        response = self.client.get(self.login_url)
        self.csrf_token = response.cookies['csrftoken']
