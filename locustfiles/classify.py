from locust import HttpUser, SequentialTaskSet, task

from data.utils import get_simulated_data


class ClassifyHTMLTasks(SequentialTaskSet):
    """
    Get the csrf token and then request classification non-stop,
    meant for estimating server capacity for classification via HTML front-end.
    """
    csrf_token = None

    def on_start(self):
        response = self.client.get("/")
        self.csrf_token = response.cookies['csrftoken']

    @task
    def classify(self):
        self.client.post(
            "/", get_simulated_data(),
            headers={"X-CSRFToken": self.csrf_token}
        )


class ClassifyHTML(HttpUser):
    tasks = [ClassifyHTMLTasks, ]
