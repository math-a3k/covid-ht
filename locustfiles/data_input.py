from os import environ

from locust import HttpUser, SequentialTaskSet, task

from locustfiles.utils import LoginTaskSetMixin, get_hemogram_data


class DataInputHTMLTasks(LoginTaskSetMixin, SequentialTaskSet):
    """
    Log in and then start inputting data non-stop, meant for estimating
    server capacity for data input via HTML front-end.
    """
    csrf_token = None
    login_url = "/accounts/login"
    user_username = environ.get("CHTLT_USER_USERNAME", "staff")
    user_password = environ.get("CHTLT_USER_PASSWORD", "staff")

    def on_start(self):
        self.login()

    @task
    def data_input(self):
        self.client.post(
            "/data/input", get_hemogram_data(for_input=True),
            headers={"X-CSRFToken": self.csrf_token}
        )


class DataInputHTML(HttpUser):
    tasks = [DataInputHTMLTasks, ]
