from random import randint
import time

from locust import HttpUser, SequentialTaskSet, task

from data.utils import get_simulated_data


class DoctorTasks(SequentialTaskSet):
    """
    The doctor will fill the HTML form for classification
    in about 2 to 3 minutes, request the classification, finish
    current attention and wait for another patient in about 20 to 30 minutes.
    """
    csrf_token = None

    @task
    def request_html_form(self):
        response = self.client.get("/")
        self.csrf_token = response.cookies['csrftoken']

    @task
    def fill_the_html_form(self):
        time.sleep(randint(2 * 60, 3 * 60))

    @task
    def submit_data(self):
        self.client.post(
            "/", get_simulated_data(),
            headers={"X-CSRFToken": self.csrf_token}
        )

    @task
    def finish_patient_and_wait_for_another(self):
        time.sleep(randint(15 * 60, 30 * 60))


class Doctor(HttpUser):
    tasks = [DoctorTasks, ]
