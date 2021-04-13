from os import environ

from locust import HttpUser, SequentialTaskSet, task

from locustfiles.utils import get_hemogram_data


class ClassifyRESTAPITasks(SequentialTaskSet):
    """
    Post data for classification non-stop, meant for estimating
    server capacity for classification via REST API.
    """
    user_auth_token = environ.get(
        "CHTLT_USER_AUTH_TOKEN", "TheQuickBrownFox..."
    )

    @task
    def classify(self):
        data = get_hemogram_data(include_label=False)
        self.client.post(
            "/api/v1/classify", data=data,
            headers={"Authorization": "Token {}".format(self.user_auth_token)}
        )


class ClassifyRESTAPI(HttpUser):
    tasks = [ClassifyRESTAPITasks, ]
