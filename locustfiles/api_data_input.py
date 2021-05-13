from os import environ

from locust import HttpUser, SequentialTaskSet, task

from data.utils import get_hemogram_data


class DataInputRESTAPITasks(SequentialTaskSet):
    """
    Post data input non-stop, meant for estimating
    server capacity for data input via REST API.
    """
    user_auth_token = environ.get(
        "CHTLT_USER_AUTH_TOKEN", "TheQuickBrownFox..."
    )

    @task
    def data_input(self):
        data = get_hemogram_data(for_input=True)
        self.client.post(
            "/api/v1/data", data=data,
            headers={"Authorization": "Token {}".format(self.user_auth_token)}
        )


class DataInputRESTAPI(HttpUser):
    tasks = [DataInputRESTAPITasks, ]
