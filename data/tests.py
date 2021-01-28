#
from decimal import Decimal

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from rest_framework.test import APITestCase

from base.models import User
from units.models import Unit

from .models import Data
from .serializers import (DataInputSerializer, DataListSerializer, )


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
        self.user2, _ = User.objects.get_or_create(
            username='testuser3',
            first_name='Test',
            last_name='User 3',
            user_type=User.MANAGER,
        )
        self.user2.set_password("test")
        self.user2.save()
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

    def test_data_input_percentages(self):
        self.user.unit = self.unit
        self.user.save()
        post_data = {
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'p_neut': Decimal("10"),
            'p_lymp': Decimal("15"),
            'p_mono': Decimal("20"),
            'p_eo': Decimal("20"),
            'p_baso': Decimal("20"),
            '_addanother': True
        }
        expected_data = {
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'neut': Decimal("0.5"),
            'lymp': Decimal("0.75"),
            'mono': Decimal("1"),
            'eo': Decimal("1"),
            'baso': Decimal("1"),
        }
        response = self.client.post(
            reverse("data:input"),
            post_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        data = Data.objects.last()
        for key in expected_data:
            self.assertEqual(getattr(data, key), expected_data[key])

    def test_data_input_invalid_form(self):
        self.user.unit = self.unit
        self.user.save()
        post_data = {
            'rbc': Decimal("33"),
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
        self.assertContains(response, 'Errors')

    def test_public_list_no_data(self):
        response = self.client.get(
            reverse("data:public-list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No data available.')

    def test_public_list(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=3, wbc=5, plt=200, neut=1
        )
        response = self.client.get(
            reverse("data:public-list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<b>Dataset Size</b>: 1")
        self.assertContains(response, data.uuid)
        self.assertContains(response, "<td>Yes</td>")
        self.assertContains(response, "<td>3.000</td>")
        self.assertContains(response, "<td>5.000</td>")
        self.assertContains(response, "<td>200</td>")
        self.assertContains(response, "<td>1.00</td>")
        self.assertContains(response, "<td>Not Available</td>")

    def test_csv(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.5, wbc=5.5, plt=220, neut=1.2
        )
        expected_response = (
            'id,unit,timestamp,uuid,is_covid19,age,sex,'
            'is_diabetic,is_hypertense,is_overweight,is_at_altitude,'
            'is_with_other_conds,rbc,wbc,hgb,hct,mcv,mch,mchc,rdw,plt,neut,'
            'lymp,mono,eo,baso,iga,igm\r\n{2},{3},{0},{1},'
            'False,,,,,,,,3.500,5.500,,,,,,,'
            '220,1.20,,,,,,\r\n'
        ).format(
            data.timestamp.strftime("%Y-%m-%d %H:%M"), data.uuid, data.id,
            data.unit.id
        )
        response = self.client.get(
            reverse("data:csv"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "attachment; filename=covid-ht-data-",
            response.get('Content-Disposition')
        )
        self.assertEqual(response.content, bytes(expected_response, 'utf-8'))

    def test_detail(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.6, wbc=5.6, plt=222, neut=1.2
        )
        response = self.client.get(
            data.url(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data.uuid)

    def test_edit(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.8, wbc=5.8, plt=223, neut=1.3
        )
        response = self.client.post(
            reverse("data:edit", args=[data.uuid, ]),
            {
                'rbc': 3.9
            }
        )
        self.assertEqual(response.status_code, 302)
        data.refresh_from_db()
        self.assertEqual(data.rbc, Decimal("3.9"))

    def test_edit_invalid_form(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.76, wbc=5.8, plt=223, neut=1.3
        )
        response = self.client.post(
            reverse("data:edit", args=[data.uuid, ]),
            {
                'rbc': 15.9
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Errors prevented saving the data')

    def test_edit_404(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.1, wbc=5.1, plt=225, neut=1.3
        )
        self.client.login(username="testuser3", password="test")
        response = self.client.get(
            reverse("data:edit", args=[data.uuid, ]),
            {
                'rbc': 3.9
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_get(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.1, wbc=5.1, plt=225, neut=1.3
        )
        response = self.client.get(
            reverse("data:edit", args=[data.uuid, ])
        )
        self.assertEqual(response.status_code, 200)


class TestDataRESTAPI(APITestCase):

    def setUp(self):
        self.unit, _ = Unit.objects.get_or_create(
            name="Unit for API tests 1"
        )
        self.user, _ = User.objects.get_or_create(
            username='apitestuser1',
            first_name='Api Test',
            last_name='User 1',
            user_type=User.DATA,
            unit=self.unit
        )
        self.user.set_password("test")
        self.user.save()
        self.user2, _ = User.objects.get_or_create(
            username='apitestuser2',
            first_name='Api Test',
            last_name='User 2',
            user_type=User.MANAGER,
        )
        self.user2.set_password("test")
        self.user2.save()
        self.client.login(username=self.user.username, password="test")

    def test_data_list(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=2, wbc=3, plt=240, neut=1
        )
        response = self.client.get(
            reverse("rest-api:data-lc"),
        )
        serializer = DataListSerializer(data)
        self.assertEqual(dict(response.data['results'][0]), serializer.data)

    def test_data_list_unpaginated(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=2, wbc=3, plt=240, neut=1
        )
        response = self.client.get(
            reverse("rest-api:data-lc"), {'page': 'no'}
        )
        serializer = DataListSerializer(data)
        self.assertEqual(response.data[0], serializer.data)

    def test_data_creation(self):
        post_data = {
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'neut': Decimal("0.1"),
            'lymp': Decimal("0.1"),
            'mono': Decimal("0.1"),
        }
        response = self.client.post(
            reverse("rest-api:data-lc"),
            post_data,
        )
        self.assertEqual(response.status_code, 201)
        data = Data.objects.last()
        for key in post_data:
            self.assertEqual(getattr(data, key), post_data[key])
        # Test also the serialization in the response
        serializer = DataInputSerializer(data)
        self.assertEqual(response.data, serializer.data)

    def test_data_creation_only_tags(self):
        post_data = {
            'is_covid19': True,
            'unit_ii': '123.123.123-4'
        }
        response = self.client.post(
            reverse("rest-api:data-lc"),
            post_data,
        )
        self.assertEqual(response.status_code, 201)
        data = Data.objects.last()
        for key in post_data:
            self.assertEqual(getattr(data, key), post_data[key])
        # Test also the serialization in the response
        serializer = DataInputSerializer(data)
        self.assertEqual(response.data, serializer.data)

    def test_data_creation_percentages(self):
        post_data = {
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'p_neut': Decimal("10"),
            'p_lymp': Decimal("15"),
            'p_mono': Decimal("20"),
            'p_eo': Decimal("20"),
            'p_baso': Decimal("20"),
        }
        expected_data = {
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'neut': Decimal("0.5"),
            'lymp': Decimal("0.75"),
            'mono': Decimal("1"),
            'eo': Decimal("1"),
            'baso': Decimal("1"),
        }
        response = self.client.post(
            reverse("rest-api:data-lc"),
            post_data,
        )
        self.assertEqual(response.status_code, 201)
        data = Data.objects.last()
        for key in expected_data:
            self.assertEqual(getattr(data, key), expected_data[key])
        # Test also the serialization in the response
        serializer = DataInputSerializer(data)
        self.assertEqual(response.data, serializer.data)

    def test_data_creation_percentages_invalid(self):
        post_data = {
            'rbc': Decimal("3"),
            'plt': Decimal("150"),
            'p_neut': Decimal("10"),
            'p_lymp': Decimal("15"),
            'p_mono': Decimal("20"),
            'p_eo': Decimal("20"),
            'p_baso': Decimal("20"),
        }
        response = self.client.post(
            reverse("rest-api:data-lc"),
            post_data,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('WBC', response.data['non_field_errors'][0])
