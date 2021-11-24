from os import environ

from locust import HttpUser, SequentialTaskSet, task

from data.utils import get_simulated_data


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
        data = get_simulated_data(for_input=False)
        self.client.post(
            "/api/v1/classify", data=data,
            headers={"Authorization": "Token {}".format(self.user_auth_token)}
        )


class ClassifyRESTAPI(HttpUser):
    tasks = [ClassifyRESTAPITasks, ]
