from copy import deepcopy
from decimal import Decimal
from importlib import reload
import json

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, Client
from django.urls import reverse

from base.models import User
import data.forms as data_forms
from units.models import Unit

from .models import Data
from .serializers import (DataInputSerializer, DataListSerializer, )


class TestData(SimpleTestCase):
    databases = "__all__"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unit, _ = Unit.objects.get_or_create(
            name="Unit for tests 2"
        )
        cls.user, _ = User.objects.get_or_create(
            username='testuser2',
            first_name='Test',
            last_name='User 2',
            user_type=User.DATA,
            unit=cls.unit
        )
        cls.user.set_password("test")
        cls.user.save()
        #
        cls.client = Client()
        cls.client.force_login(user=cls.user)
        #
        cls.user2, _ = User.objects.get_or_create(
            username='testuser3',
            first_name='Test',
            last_name='User 3',
            user_type=User.MANAGER,
        )
        cls.user2.set_password("test")
        cls.user2.save()

    def test_is_allowed_in_data_privacy_mode(self):
        # Test Public Access
        with self.settings(DATA_PRIVACY_MODE=False):
            response = self.client.get(
                reverse("data:public-list"),
            )
            self.assertEqual(response.status_code, 200)
            response = self.client.get(
                reverse("data:csv"),
            )
        self.assertEqual(response.status_code, 200)
        # Test Restricted Access
        self.client.logout()
        response = self.client.get(
            reverse("data:public-list"),
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(
            reverse("data:csv"),
        )
        self.assertEqual(response.status_code, 302)
        # Test Logged-In Access
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse("data:public-list"),
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse("data:csv"),
        )
        self.assertEqual(response.status_code, 200)
        self.client.force_login(user=self.user)

    def test_data_input_no_unit(self):
        client = deepcopy(self.client)
        self.user.unit = None
        self.user.save()
        client.force_login(user=self.user)
        response = client.get(
            reverse("data:input"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A unit must be selected for a User')
        self.user.unit = self.unit
        self.user.save()

    def test_data_input(self):
        self.client.force_login(user=self.user)
        post_data = {
            'unit_ii': "test_data_input",
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
        data = Data.objects.get(unit_ii="test_data_input")
        for key in post_data:
            self.assertEqual(getattr(data, key), post_data[key])

    def test_data_input_percentages(self):
        self.client.force_login(user=self.user)
        post_data = {
            'unit_ii': "test_data_input_percentages",
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'neut_Upercentage_Rwbc': Decimal("10"),
            'lymp_Upercentage_Rwbc': Decimal("15"),
            'mono_Upercentage_Rwbc': Decimal("20"),
            'eo_Upercentage_Rwbc': Decimal("20"),
            'baso_Upercentage_Rwbc': Decimal("20"),
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
        data = Data.objects.get(unit_ii='test_data_input_percentages')
        for key in expected_data:
            self.assertEqual(getattr(data, key), expected_data[key])

    def test_data_conversions(self):
        self.client.force_login(user=self.user)
        post_data = {
            'unit_ii': "test_data_conversions",
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'hgb_UmmolL': Decimal("2"),
            'hgbp_UumolL': Decimal("1.4"),
            'mch_Ufmolcell': Decimal("1"),
            'mchc_UgdL': Decimal("30"),
            'mchc_UmmolL': Decimal("4"),
            'rtc_Upercentage_Rrbc': Decimal("20"),
            'atb_UmgmL': Decimal("1.32"),
            'aat_UumolL': Decimal("50"),
        }
        expected_data = {
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'hgb': Decimal("3"),
            'hgbp': Decimal("8"),
            'mch': Decimal("16"),
            'mchc': Decimal("6"),
            'rtc': Decimal("0.6"),
            'atb': Decimal("7"),
            'aat': Decimal("31"),
        }
        response = self.client.post(
            reverse("data:input"),
            post_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        data = Data.objects.get(unit_ii="test_data_conversions")
        for key in expected_data:
            self.assertEqual(getattr(data, key), expected_data[key])

    def test_data_input_invalid_form(self):
        self.client.force_login(user=self.user)
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
        self.client.force_login(user=self.user)
        Data.objects.all().delete()
        response = self.client.get(
            reverse("data:public-list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No data available.')

    def test_public_list(self):
        self.client.force_login(user=self.user)
        Data.objects.all().delete()
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=3, wbc=5, plt=200, neut=1,
            is_finished=True
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
        self.client.force_login(user=self.user)
        Data.objects.all().delete()
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.5, wbc=5.5, plt=220, neut=1.2,
            is_finished=True
        )
        expected_response = (
            'chtuid,unit,timestamp,uuid,is_covid19,rbc,wbc,hgb,hgbp,hgbg,htg,'
            'hct,mcv,mch,mchc,rdw,rtc,plt,mpv,pt,inr,aptt,tct,fbg,atb,bt,vsy,'
            'esr,crp,aat,pct,neut,nbf,lymp,mono,mnl,cd4,eo,baso,iga,igd,ige,'
            'igg,igm\r\n'
            'cHT00,{2},{0},{1},'
            'False,3.500,5.500,,,,,,,,,,,220,,,,,,,,,,,,,,1.20,,,,,,,,,,,,\r\n'
        ).format(
            data.timestamp.strftime("%Y-%m-%d %H:%M"), data.uuid,
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
        self.client.force_login(user=self.user)
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
        self.client.force_login(user=self.user)
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
        self.client.force_login(user=self.user)
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
        self.client.force_login(user=self.user)
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.1, wbc=5.1, plt=225, neut=1.3
        )
        response = self.client.get(
            reverse("data:edit", args=[data.uuid, ])
        )
        self.assertEqual(response.status_code, 200)

    def test_data_clean(self):
        data = Data(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.1, wbc=5.1, plt=225, neut=1.3
        )
        data.clean()
        with self.assertRaises(ValidationError):
            data.is_covid19 = None
            data.is_finished = True
            data.clean()

    def test_data_classification_form_fields_setting(self):
        with self.settings(
                DATA_CLASSIFICATION_FORM_FIELDS=['rbc', 'hgb', 'hgb_UmmolL']
                ):
            reload(data_forms)
            self.assertTrue(
                'rbc' in data_forms.DataClassificationForm().fields
            )
            self.assertTrue(
                'wbc' not in data_forms.DataClassificationForm().fields
            )
        with self.settings(
                DATA_CLASSIFICATION_FORM_FIELDS='__all__'
                ):
            reload(data_forms)
            expected_fields = Data.AUXILIARY_FIELDS + \
                Data.get_hemogram_main_fields() + \
                Data.get_conversion_fields()
            for field in expected_fields:
                self.assertTrue(
                    field in data_forms.DataClassificationForm().fields
                )

    def test_data_input_form_fields_setting(self):
        with self.settings(
                DATA_INPUT_FORM_FIELDS=['rbc', 'hgb', 'hgb_UmmolL']
                ):
            reload(data_forms)
            self.assertTrue('rbc' in data_forms.DataInputForm().fields)
            self.assertTrue('wbc' not in data_forms.DataInputForm().fields)

    def test_data_apply_conversion_fields_rules_to_dict(self):
        data = {
            'rbc': Decimal('3.5'),
            'wbc': Decimal(3),
            'hgb_UmmolL': Decimal(2),
            'lymp_Upercentage_Rwbc': Decimal(10)
        }
        expected_result = {
            'rbc': Decimal('3.5'),
            'wbc': Decimal(3),
            'hgb': Decimal(2) * Decimal('1.62'),
            'hgb_UmmolL': Decimal(2),
            'lymp': Decimal('0.3'),
            'lymp_Upercentage_Rwbc': Decimal(10)
        }
        result = Data.apply_conversion_fields_rules_to_dict(data)
        self.assertEqual(expected_result, result)

    def test_rest_api_data_list(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=2, wbc=3, plt=240, neut=1
        )
        response = self.client.get(
            reverse("rest-api:data-lc"),
        )
        serializer = DataListSerializer(data)
        self.assertEqual(dict(response.data['results'][0]), serializer.data)

    def test_rest_api_data_list_unpaginated(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=True, rbc=2, wbc=3, plt=240, neut=1
        )
        response = self.client.get(
            reverse("rest-api:data-lc"), {'page': 'no'}
        )
        serializer = DataListSerializer(data)
        self.assertEqual(response.data[0], serializer.data)

    def test_rest_api_data_creation(self):
        self.client.force_login(user=self.user)
        post_data = {
            'unit_ii': 'test_rest_api_data_creation',
            'is_finished': False,
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

    def test_rest_api_data_creation_not_authenticated(self):
        self.client.logout()
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
        self.assertEqual(response.status_code, 403)
        self.client.force_login(user=self.user)

    def test_rest_api_data_creation_only_tags(self):
        self.client.force_login(user=self.user)
        post_data = {
            'is_covid19': True,
            'unit_ii': '123.123.123-4',
            'is_finished': False
        }
        response = self.client.post(
            reverse("rest-api:data-lc"),
            post_data,
              )
        self.assertEqual(response.status_code, 201)
        data = Data.objects.get(unit_ii='123.123.123-4')
        for key in post_data:
            self.assertEqual(getattr(data, key), post_data[key])
        # Test also the serialization in the response
        serializer = DataInputSerializer(data)
        self.assertEqual(response.data, serializer.data)

    def test_rest_api_data_creation_percentages(self):
        self.client.force_login(user=self.user)
        post_data = {
            'unit_ii': 'test_rest_api_data_creation_percentages',
            'is_finished': False,
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'neut_Upercentage_Rwbc': Decimal("10"),
            'lymp_Upercentage_Rwbc': Decimal("15"),
            'mono_Upercentage_Rwbc': Decimal("20"),
            'eo_Upercentage_Rwbc': Decimal("20"),
            'baso_Upercentage_Rwbc': Decimal("20"),
        }
        expected_data = {
            'is_finished': False,
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
        data = Data.objects.get(
            unit_ii='test_rest_api_data_creation_percentages'
        )
        for key in expected_data:
            self.assertEqual(getattr(data, key), expected_data[key])
        # Test also the serialization in the response
        serializer = DataInputSerializer(data)
        self.assertEqual(response.data, serializer.data)

    def test_rest_api_data_creation_percentages_invalid(self):
        self.client.force_login(user=self.user)
        post_data = {
            'is_finished': False,
            'rbc': Decimal("3"),
            'plt': Decimal("150"),
            'neut_Upercentage_Rwbc': Decimal("10"),
            'lymp_Upercentage_Rwbc': Decimal("15"),
            'mono_Upercentage_Rwbc': Decimal("20"),
            'eo_Upercentage_Rwbc': Decimal("20"),
            'baso_Upercentage_Rwbc': Decimal("20"),
        }
        response = self.client.post(
            reverse("rest-api:data-lc"),
            post_data,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('This field must be present', response.data['wbc'][0])

    def test_rest_api_network_sharing(self):
        # -> Test receiving data from the network's nodes
        self.client.force_login(user=self.user)
        put_data = {
            'chtuid': 'abc01',
            'uuid': '4e9b03f7-96bf-4386-804f-bdbe7aef1691',
            'rbc': Decimal("3"),
            'plt': Decimal("150"),
            'wbc': Decimal("3"),
            'lymp_Upercentage_Rwbc': Decimal("15"),
            'mono_Upercentage_Rwbc': Decimal("20"),
            'eo_Upercentage_Rwbc': Decimal("20"),
            'baso_Upercentage_Rwbc': Decimal("20"),
        }
        response = self.client.put(
            reverse("rest-api:data-lc"),
            put_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        # Repeat the request to test update
        response = self.client.put(
            reverse("rest-api:data-lc"),
            put_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        # Test PATCH
        response = self.client.patch(
            reverse("rest-api:data-lc"),
            put_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        patch_data = {
            'chtuid': 'abc01',
            'uuid': '4e9b03f7-96bf-2222-804f-bdbe7aef1691',
            'rbc': Decimal("3"),
            'plt': Decimal("150"),
            'wbc': Decimal("3"),
            'lymp_Upercentage_Rwbc': Decimal("15"),
            'mono_Upercentage_Rwbc': Decimal("20"),
            'eo_Upercentage_Rwbc': Decimal("20"),
            'baso_Upercentage_Rwbc': Decimal("20"),
        }
        response = self.client.patch(
            reverse("rest-api:data-lc"),
            patch_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        # -> Test echo from the network
        Data.objects.create(
            uuid='4e9b03f7-96bf-4386-0000-bdbe7aef1691',
            user=self.user, unit=self.unit,
        )
        put_data = {
            'chtuid': 'cHT00',
            'uuid': '4e9b03f7-96bf-4386-0000-bdbe7aef1691',
            'rbc': Decimal("3"),
            'plt': Decimal("150"),
            'wbc': Decimal("3"),
            'lymp_Upercentage_Rwbc': Decimal("15"),
            'mono_Upercentage_Rwbc': Decimal("20"),
            'eo_Upercentage_Rwbc': Decimal("20"),
            'baso_Upercentage_Rwbc': Decimal("20"),
        }
        response = self.client.put(
            reverse("rest-api:data-lc"),
            put_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 208)

    def test_rest_api_data_detail(self):
        self.client.force_login(user=self.user)
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.7, wbc=5.8, plt=223, neut=1.3
        )
        response = self.client.get(
            reverse("rest-api:data-ru", args=[data.uuid, ]),
        )
        self.assertEqual(response.status_code, 200)
        data_dict = json.loads(response.content)
        serializer = DataInputSerializer(data)
        self.assertEqual(data_dict, serializer.data)

    def test_rest_api_data_edit(self):
        self.client.force_login(user=self.user)
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.7, wbc=5.8, plt=223, neut=1.3
        )
        response = self.client.patch(
            reverse("rest-api:data-ru", args=[data.uuid, ]),
            {
                'rbc': 3.9
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data.refresh_from_db()
        self.assertEqual(data.rbc, Decimal("3.9"))

    def test_rest_api_edit_not_authenticated(self):
        self.client.logout()
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.6, wbc=5.8, plt=223, neut=1.3
        )
        response = self.client.patch(
            reverse("rest-api:data-ru", args=[data.uuid, ]),
            {
                'rbc': 3.9
            }
        )
        self.assertEqual(response.status_code, 403)
        data.refresh_from_db()
        self.assertEqual(data.rbc, Decimal("3.6"))
        self.client.force_login(user=self.user)

    def test_rest_api_data_edit_not_owner(self):
        data, _ = Data.objects.get_or_create(
            user=self.user, unit=self.unit,
            is_covid19=False, rbc=3.6, wbc=5.8, plt=223, neut=1.3
        )
        self.client.login(username="apitestuser2", password="test")
        response = self.client.patch(
            reverse("rest-api:data-ru", args=[data.uuid, ]),
            {
                'rbc': 3.9
            }
        )
        self.assertEqual(response.status_code, 403)
        data.refresh_from_db()
        self.assertEqual(data.rbc, Decimal("3.6"))
