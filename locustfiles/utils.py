

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
