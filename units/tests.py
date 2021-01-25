#
from copy import deepcopy

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from base.models import User
from data.models import Data

from .models import Unit


class TestUnits(StaticLiveServerTestCase):

    def setUp(self):
        self.unit, _ = Unit.objects.get_or_create(
            name="Unit for tests 3"
        )
        self.unit2, _ = Unit.objects.get_or_create(
            name="Unit for tests 4"
        )
        self.user, _ = User.objects.get_or_create(
            username='testuser3',
            first_name='Test',
            last_name='User 3',
            user_type=User.MANAGER,
            unit=self.unit,
        )
        self.user.set_password("test")
        self.user.save()
        self.user2, _ = User.objects.get_or_create(
            username='testuser4',
            first_name='Test',
            last_name='User 4',
            user_type=User.DATA,
            unit=self.unit,
        )
        self.user2.set_password("test")
        self.user2.save()
        self.client.login(username=self.user.username, password="test")

    def test_list(self):
        response = self.client.get(
            reverse("units:list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unit for tests 3')
        self.assertContains(response, '<td>0</td>')

    def test_detail_no_data(self):
        response = self.client.get(
            reverse("units:detail", args=[self.unit.pk, ]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unit for tests 3')
        self.assertContains(response, '<b>Dataset Size</b>: 0')
        self.assertContains(response, '<b>Managers</b>: 1')
        self.assertContains(response, '<b>Data Input</b>: 1')

    def test_detail(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=2, wbc=4, plt=200, neut=1
        )

        response = self.client.get(
            self.unit.url()
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unit for tests 3')
        self.assertContains(response, '<b>Dataset Size</b>: 1')

    def test_unit_dashboard(self):
        response = self.client.get(
            reverse("units:current:dashboard"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '{0} Dashboard'.format(self.unit.name))

    def test_unit_dashboard_with_data(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=5, wbc=2, plt=200, neut=1
        )
        response = self.client.get(
            reverse("units:current:dashboard"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '{0} Dashboard'.format(self.unit.name))

    def test_unit_dashboard_no_unit(self):
        self.user.unit = None
        self.user.save()
        response = self.client.get(
            reverse("units:current:dashboard"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Unit has been selected')
        self.user.unit = self.unit
        self.user.save()

    def test_unit_edit(self):
        response = self.client.get(
            reverse("units:current:edit"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editing Unit')

    def test_unit_edit_post(self):
        response = self.client.post(
            reverse("units:current:edit"),
            {
                'name': "Test Test Unit",
                'description': "Test Description",
                'timezone': "America/Lima"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.unit.refresh_from_db()
        self.assertEqual(self.unit.name, "Test Test Unit")

    def test_unit_edit_post_invalid(self):
        response = self.client.post(
            reverse("units:current:edit"),
            {
                'name': "Test Test Unit",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid')

    def test_unit_user_list(self):
        response = self.client.get(
            reverse("units:current:users-list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unit\'s Members')
        self.assertContains(response, 'USER 3')
        self.assertContains(response, 'USER 4')

    def test_unit_user_detail(self):
        response = self.client.get(
            reverse("units:current:users-detail", args=[self.user.pk, ]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST USER 3')

    def test_unit_user_detail_from_other_unit(self):
        self.user2.unit = self.unit2
        self.user2.save()
        response = self.client.get(
            reverse("units:current:users-detail", args=[self.user2.pk, ]),
        )
        self.assertEqual(response.status_code, 404)
        self.user2.unit = self.unit
        self.user2.save()

    def test_unit_user_edit(self):
        response = self.client.get(
            reverse("units:current:users-edit", args=[self.user.pk, ]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editing User')

    def test_unit_user_edit_post(self):
        response = self.client.post(
            reverse("units:current:users-edit", args=[self.user.pk, ]),
            {
                "user_type": User.MANAGER,
                "first_name": "TEST edit",
                "last_name": "User 3",
                "username": "testuser3",
                "email": "test3@test.com"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "TEST EDIT")

    def test_unit_user_edit_post_invalid(self):
        response = self.client.post(
            reverse("units:current:users-edit", args=[self.user.pk, ]),
            {
                "first_name": "TEST edit",
                "last_name": "User 3",
                "email": "test3@test.com"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid')

    def test_unit_user_edit_from_other_unit(self):
        self.user2.unit = self.unit2
        self.user2.save()
        response = self.client.get(
            reverse("units:current:users-edit", args=[self.user2.pk, ]),
        )
        self.assertEqual(response.status_code, 404)
        self.user2.unit = self.unit
        self.user2.save()

    def test_unit_user_new(self):
        response = self.client.get(
            reverse("units:current:users-new", ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Unit User')

    def test_unit_user_new_post(self):
        new_user = {
            "user_type": User.MANAGER,
            "first_name": "TEST",
            "last_name": "USER 5",
            "username": "testuser5",
            "email": "test5@test.com",
            'password1': "testpassword",
            'password2': "testpassword",
        }
        response = self.client.post(
            reverse("units:current:users-new",),
            new_user
        )
        self.assertEqual(response.status_code, 302)
        last_user = User.objects.last()
        new_user.pop('password1')
        new_user.pop('password2')
        for key in new_user:
            self.assertEqual(getattr(last_user, key), new_user[key])

    def test_unit_user_new_post_invalid(self):
        response = self.client.post(
            reverse("units:current:users-new", ),
            {
                "first_name": "TEST",
                "last_name": "User 5",
                "email": "test5@test.com"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid')

    def test_unit_user_set_password(self):
        response = self.client.get(
            reverse("units:current:users-set-password", args=[self.user.pk, ]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Set password for')

    def test_unit_user_set_password_post(self):
        user_copy = deepcopy(self.user)
        user_copy.set_password("n3w.p4ssw0rd.t3st1ng")
        response = self.client.post(
            reverse("units:current:users-set-password", args=[self.user.pk, ]),
            {
                "new_password1": "n3w.p4ssw0rd.t3st1ng",
                "new_password2": "n3w.p4ssw0rd.t3st1ng",
            }
        )
        self.assertEqual(response.status_code, 302)
        login_result = self.client.login(
            username=self.user.username, password="n3w.p4ssw0rd.t3st1ng"
        )
        self.assertEqual(login_result, True)

    def test_unit_user_set_password_post_invalid(self):
        response = self.client.post(
            reverse("units:current:users-set-password", args=[self.user.pk, ]),
            {
                "new_password1": "newpassword",
                "new_password2": "oldpassword",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid')

    def test_unit_user_set_password_from_other_unit(self):
        self.user2.unit = self.unit2
        self.user2.save()
        response = self.client.get(
            reverse("units:current:users-set-password", args=[self.user2.pk, ])
        )
        self.assertEqual(response.status_code, 404)
        self.user2.unit = self.unit
        self.user2.save()

    def test_csv(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=2.5, wbc=3.5, plt=220, neut=1.2
        )
        expected_response = (
            'id,user,timestamp,unit_ii,is_covid19,age,sex,is_diabetic,'
            'is_hypertense,is_overweight,is_at_altitude,is_with_other_conds,'
            'rbc,wbc,hgb,hct,mcv,mch,mchc,rdw,plt,neut,lymp,mono,eo,baso,iga,'
            'igm\r\n{2},{1},{0},,False,,,,,,,,2.500,3.500,'
            ',,,,,,220,1.20,,,,,,\r\n'
        ).format(
            data.timestamp.strftime("%Y-%m-%d %H:%M"), data.user.name, data.id
        )
        response = self.client.get(
            reverse("units:current:data-csv"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "attachment; filename=covid-ht-unit-",
            response.get('Content-Disposition')
        )
        self.assertEqual(response.content, bytes(expected_response, 'utf-8'))

    def test_unit_data_no_data(self):
        response = self.client.get(
            reverse("units:current:data"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No data available.')

    def test_unit_data(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=3, wbc=5, plt=200, neut=1
        )
        response = self.client.get(
            reverse("units:current:data"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<b>Dataset Size</b>: 1")
        self.assertContains(response, data.user.name)
        self.assertContains(response, "<td>Yes</td>")
        self.assertContains(response, "<td>3.000</td>")
        self.assertContains(response, "<td>5.000</td>")
        self.assertContains(response, "<td>200</td>")
        self.assertContains(response, "<td>1.00</td>")
        self.assertContains(response, "<td>Not Available</td>")
