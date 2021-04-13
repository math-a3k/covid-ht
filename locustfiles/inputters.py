from os import environ
from random import randint, seed
import time

from locust import HttpUser, SequentialTaskSet, task

from locustfiles.utils import LoginTaskSetMixin, get_hemogram_data

seed(123456)


class DataInputterTasks(LoginTaskSetMixin, SequentialTaskSet):
    """
    The Inputter will log in and then will request the input HTML form,
    fill it in about 1.5 to 2.5 minutes and then wait between 15 and 30
    seconds for the next record.
    """
    csrf_token = None
    login_url = "/accounts/login/"
    user_username = environ.get("CHTLT_USER_USERNAME", "staff")
    user_password = environ.get("CHTLT_USER_PASSWORD", "staff")

    def on_start(self):
        self.login()

    @task
    def request_data_input_form(self):
        self.client.get("/data/input")

    @task
    def fill_the_html_form(self):
        time.sleep(randint(1.5 * 60, 2.5 * 60))

    @task
    def submit_data(self):
        self.client.post(
            "/data/input", get_hemogram_data(for_input=True),
            headers={"X-CSRFToken": self.csrf_token}
        )

    @task
    def find_another_record(self):
        time.sleep(randint(15, 30))


class Inputter(HttpUser):
    tasks = [DataInputterTasks, ]
