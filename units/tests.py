#
from copy import deepcopy

from django.urls import reverse
from django.test import SimpleTestCase, Client

from base.models import User
from data.models import Data

from .models import Unit


class TestUnits(SimpleTestCase):
    databases = "__all__"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unit, _ = Unit.objects.get_or_create(
            name="Unit for tests 5"
        )
        cls.unit2, _ = Unit.objects.get_or_create(
            name="Unit for tests 6"
        )
        cls.user, _ = User.objects.get_or_create(
            username='testuser5',
            first_name='Test',
            last_name='User 5',
            user_type=User.MANAGER,
            unit=cls.unit,
        )
        cls.user.set_password("test")
        cls.user.save()
        cls.user2, _ = User.objects.get_or_create(
            username='testuser6',
            first_name='Test6',
            last_name='User 6',
            user_type=User.DATA,
            unit=cls.unit,
        )
        cls.user2.set_password("test")
        cls.user2.save()
        cls.client = Client()
        cls.client.login(username=cls.user.username, password="test")

    def test_list(self):
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unit for tests 5')
        self.assertContains(response, '<td>0</td>')

    def test_detail_no_data(self):
        Data.objects.all().delete()
        response = self.client.get(
            reverse("units:detail", args=[self.unit.pk, ]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unit for tests 5')
        self.assertContains(response, '<b>Dataset Size</b>: 0')
        self.assertContains(response, '<b>Managers</b>: 1')
        self.assertContains(response, '<b>Data Input</b>: 1')

    def test_detail(self):
        self.client.force_login(user=self.user)
        Data.objects.all().delete()
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=2, wbc=4, plt=200, neut=1
        )

        response = self.client.get(
            self.unit.url()
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unit for tests 5')
        self.assertContains(response, '<b>Dataset Size</b>: 1')

    def test_unit_dashboard(self):
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:dashboard"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '{0} Dashboard'.format(self.unit.name))

    def test_unit_dashboard_with_data(self):
        self.client.force_login(user=self.user)
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
        self.client.force_login(user=self.user)
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
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:edit"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editing Unit')

    def test_unit_edit_post(self):
        self.client.force_login(user=self.user)
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
        self.client.force_login(user=self.user)
        response = self.client.post(
            reverse("units:current:edit"),
            {
                'name': "Test Test Unit",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid')

    def test_unit_user_list(self):
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:users-list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unit\'s Members')
        self.assertContains(response, 'USER 5')
        self.assertContains(response, 'USER 6')

    def test_unit_user_detail(self):
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:users-detail", args=[self.user.pk, ]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST USER 5')

    def test_unit_user_detail_from_other_unit(self):
        self.user.unit = self.unit2
        self.user.save()
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:users-detail", args=[self.user2.pk, ]),
        )
        self.assertEqual(response.status_code, 404)
        self.user.unit = self.unit
        self.user.save()

    def test_unit_user_edit(self):
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:users-edit", args=[self.user.pk, ]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editing User')

    def test_unit_user_edit_post(self):
        self.client.force_login(user=self.user)
        response = self.client.post(
            reverse("units:current:users-edit", args=[self.user.pk, ]),
            {
                "user_type": User.MANAGER,
                "first_name": "TEST edit",
                "last_name": "User 5",
                "username": "testuser5",
                "email": "test3@test.com"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "TEST EDIT")

    def test_unit_user_edit_post_invalid(self):
        self.client.force_login(user=self.user)
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
        self.user.unit = self.unit2
        self.user.save()
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:users-edit", args=[self.user2.pk, ]),
        )
        self.assertEqual(response.status_code, 404)
        self.user.unit = self.unit
        self.user.save()

    def test_unit_user_new(self):
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:users-new", ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Unit User')

    def test_unit_user_new_post(self):
        self.client.force_login(user=self.user)
        new_user = {
            "user_type": User.MANAGER,
            "first_name": "TEST",
            "last_name": "USER 7",
            "username": "testuser7",
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
        self.client.force_login(user=self.user)
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
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:users-set-password", args=[self.user.pk, ]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Set password for')

    def test_unit_user_set_password_post(self):
        self.client.force_login(user=self.user)
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
        self.user.set_password("test")
        self.user.save()

    def test_unit_user_set_password_post_invalid(self):
        self.client.force_login(user=self.user)
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
        self.user.unit = self.unit2
        self.user.save()
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("units:current:users-set-password", args=[self.user2.pk, ])
        )
        self.assertEqual(response.status_code, 404)
        self.user.unit = self.unit
        self.user.save()

    def test_csv(self):
        self.client.force_login(user=self.user)
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=2.5, wbc=3.5, plt=220, neut=1.2
        )
        expected_response = (
            'id,user,timestamp,chtuid,is_finished,unit_ii,is_covid19,age,sex,'
            'is_diabetic,is_hypertense,is_overweight,is_at_altitude,'
            'is_with_other_conds,rbc,hgb,hgbp,hgbg,htg,hct,mcv,mch,mchc,rdw,'
            'rtc,plt,mpv,pt,inr,aptt,tct,fbg,atb,bt,vsy,wbc,neut,nbf,lymp,'
            'mono,mnl,cd4,eo,baso,iga,igd,ige,igg,igm,esr,crp,aat,pct\r\n'
            '{2},{1},{0}'
            ',cHT00,False,,False,,,,,,,,2.500,,,,,,,,,,,'
            '220,,,,,,,,,,3.500,1.20,,,,,,,,,,,,,,,,\r\n'
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
        self.client.force_login(user=self.user)
        Data.objects.all().delete()
        response = self.client.get(
            reverse("units:current:data"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No data available.')

    def test_unit_data(self):
        self.client.force_login(user=self.user)
        Data.objects.all().delete()
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
