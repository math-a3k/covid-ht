#
from decimal import Decimal
# from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from base.models import User
from units.models import Unit

from .models import Data


class TestData(StaticLiveServerTestCase):

    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username='testuser2',
            first_name='Test',
            last_name='User 2',
            user_type=User.DATA,
        )
        self.user.set_password("test")
        self.user.save()
        self.unit, _ = Unit.objects.get_or_create(
            name="Unit for tests 2"
        )
        self.client.login(username=self.user.username, password="test")

    def test_data_input_no_unit(self):
        response = self.client.get(
            reverse("data:input"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A unit must be selected for a User')

    def test_data_input(self):
        self.user.unit = self.unit
        self.user.save()
        post_data = {
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'neut': Decimal("0.1"),
            'lymp': Decimal("0.1"),
            'mono': Decimal("0.1"),
        }
        response = self.client.post(
            reverse("data:input"),
            post_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        data = Data.objects.last()
        for key in post_data:
            self.assertEqual(getattr(data, key), post_data[key])
