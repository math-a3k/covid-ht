#
import random
import numpy as np

from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from rest_framework.test import APITestCase

from django_ai.ai_base.models import DataColumn
from django_ai.supervised_learning.models.hgb import HGBTree

from data.utils import trunc_normal
from data.models import Data
from units.models import Unit

from .models import (User, CurrentClassifier)


class TestBase(StaticLiveServerTestCase):
    """
    """
    user = None
    unit = None

    def setUp(self):
        # Set the seeds
        random.seed(123456)
        np.random.seed(123456)
        #
        self.classifier, _ = HGBTree.objects.get_or_create(
            name="HGBTree for tests",
            labels_column="data.data.is_covid19",
            cv_folds=5,
            cv_metric="accuracy",
            random_state=123456
        )
        self.dc_1, _ = DataColumn.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(HGBTree),
            object_id=self.classifier.id,
            ref_model=ContentType.objects.get_for_model(Data),
            ref_column="is_diabetic",
            position=0,
        )
        self.dc_2, _ = DataColumn.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(HGBTree),
            object_id=self.classifier.id,
            ref_model=ContentType.objects.get_for_model(Data),
            ref_column="rbc",
            position=1,
        )
        self.dc_1, _ = DataColumn.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(HGBTree),
            object_id=self.classifier.id,
            ref_model=ContentType.objects.get_for_model(Data),
            ref_column="wbc",
            position=2,
        )
        self.unit, _ = Unit.objects.get_or_create(
            name="Unit for tests"
        )
        self.user, _ = User.objects.get_or_create(
            username='testuser',
            first_name='Test',
            last_name='User',
            user_type=User.MANAGER,
            unit=self.unit
        )
        # Populate with data
        covid_size = 600
        no_covid_size = 400
        table_size = covid_size + no_covid_size
        # Is COVID19 is ~ 35% F (0) / 65% T (1)
        is_covid19 = \
            [True for i in range(covid_size)] + \
            [False for i in range(no_covid_size)]
        # Is Diabetic is ~ 80% F (0) / 20% T (1)
        is_diabetic = np.random.binomial(1, 0.20, table_size)
        rbc = \
            trunc_normal(2, 8, 4.5, 2, covid_size) + \
            trunc_normal(2, 8, 4.3, 2, no_covid_size)
        wbc = \
            trunc_normal(2, 40, 7, 5, covid_size) + \
            trunc_normal(2, 40, 10, 5, no_covid_size)
        ds = []
        for i in range(0, table_size):
            # Add some missing data
            is_diab = is_diabetic[i] if np.random.uniform() > 0.1 else None
            ds.append(
                Data(
                    user=self.user,
                    unit=self.unit,
                    is_covid19=is_covid19[i],
                    is_diabetic=is_diab,
                    rbc=rbc[i],
                    wbc=wbc[i],
                )
            )
        Data.objects.bulk_create(ds)

    def test_no_current_classifier(self):
        """
        If no inference is performed on the classifier,
        an appropriate message is displayed.
        """
        CurrentClassifier.objects.all().delete()
        response = self.client.get(reverse("base:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Current Classifier")

    def test_no_inference(self):
        """
        If no inference is performed on the classifier,
        an appropriate message is displayed.
        """
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        response = self.client.get(reverse("base:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No training has been done yet.")

    def test_inference_available(self):
        """
        If the inference is already performed, the submit button is available.
        """
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.get(reverse("base:home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No training has been done yet.")
        self.assertContains(response,
                            ('<button class="btn waves-effect waves-light '
                             'blue darken-3" type="submit" name="action">'))

    def test_classification(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.post(
            reverse("base:home"),
            {
                'rbc': 3,
                'wbc': 5,
                'plt': 150,
                'neut': 0.1,
                'lymp': 0.1,
                'mono': 0.1,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'POSITIVE')

    def test_classification_with_percentage_fields(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.post(
            reverse("base:home"),
            {
                'rbc': 3,
                'wbc': 5,
                'plt': 150,
                'p_neut': 10,
                'p_lymp': 10,
                'p_mono': 10,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'POSITIVE')

    def test_not_enough_hemogram_fields(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.post(
            reverse("base:home"),
            {
                'rbc': 3,
                'wbc': 5,
                'plt': 150,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'hemogram result fields must be')

    def test_no_wbc_with_percentage_fields(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.post(
            reverse("base:home"),
            {
                'rbc': 3,
                'plt': 150,
                'mcv': 80,
                'mchc': 330,
                'neut': 0.1,
                'lymp': 0.1,
                'p_mono': 0.1,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'WBC must be present')

    def test_about(self):
        response = self.client.get(reverse("base:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About')


class TestBaseRESTAPI(APITestCase):

    def setUp(self):
        # Set the seeds
        random.seed(123456)
        np.random.seed(123456)
        #
        self.classifier, _ = HGBTree.objects.get_or_create(
            name="HGBTree for API tests",
            labels_column="data.data.is_covid19",
            cv_is_enabled=False,
            random_state=123456
        )
        self.dc_1, _ = DataColumn.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(HGBTree),
            object_id=self.classifier.id,
            ref_model=ContentType.objects.get_for_model(Data),
            ref_column="is_diabetic",
            position=0,
        )
        self.dc_2, _ = DataColumn.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(HGBTree),
            object_id=self.classifier.id,
            ref_model=ContentType.objects.get_for_model(Data),
            ref_column="rbc",
            position=1,
        )
        self.dc_1, _ = DataColumn.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(HGBTree),
            object_id=self.classifier.id,
            ref_model=ContentType.objects.get_for_model(Data),
            ref_column="wbc",
            position=2,
        )
        self.unit, _ = Unit.objects.get_or_create(
            name="Unit for API tests 2"
        )
        self.user, _ = User.objects.get_or_create(
            username='apitestuser3',
            first_name='Api Test',
            last_name='User 3',
            user_type=User.DATA,
            unit=self.unit
        )
        self.user.set_password("test")
        self.user.save()
        self.client.login(username=self.user.username, password="test")
        # Populate with data
        covid_size = 600
        no_covid_size = 400
        table_size = covid_size + no_covid_size
        # Is COVID19 is ~ 35% F (0) / 65% T (1)
        is_covid19 = \
            [True for i in range(covid_size)] + \
            [False for i in range(no_covid_size)]
        # Is Diabetic is ~ 80% F (0) / 20% T (1)
        is_diabetic = np.random.binomial(1, 0.20, table_size)
        rbc = \
            trunc_normal(2, 8, 4.5, 2, covid_size) + \
            trunc_normal(2, 8, 4.3, 2, no_covid_size)
        wbc = \
            trunc_normal(2, 40, 7, 5, covid_size) + \
            trunc_normal(2, 40, 10, 5, no_covid_size)
        ds = []
        for i in range(0, table_size):
            # Add some missing data
            is_diab = is_diabetic[i] if np.random.uniform() > 0.1 else None
            ds.append(
                Data(
                    user=self.user,
                    unit=self.unit,
                    is_covid19=is_covid19[i],
                    is_diabetic=is_diab,
                    rbc=rbc[i],
                    wbc=wbc[i],
                )
            )
        Data.objects.bulk_create(ds)

    def test_no_current_classifier(self):
        CurrentClassifier.objects.all().delete()
        response = self.client.post(
            reverse("rest-api:classify"),
            {
                'rbc': 3,
                'wbc': 5,
                'plt': 150,
                'neut': 0.1,
                'lymp': 0.1,
                'mono': 0.1,
            }
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.content, b'{"detail":"Classification Unavailable"}'
        )

    def test_no_inference(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        response = self.client.post(
            reverse("rest-api:classify"),
            {
                'rbc': 3,
                'wbc': 5,
                'plt': 150,
                'neut': 0.1,
                'lymp': 0.1,
                'mono': 0.1,
            }
        )
        self.assertEqual(response.status_code, 503)
        self.classifier.perform_inference()

    def test_classification(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.post(
            reverse("rest-api:classify"),
            {
                'rbc': 3,
                'wbc': 5,
                'plt': 150,
                'neut': 0.1,
                'lymp': 0.1,
                'mono': 0.1,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'POSITIVE', response.content)

    def test_classification_with_percentage_fields(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.post(
            reverse("rest-api:classify"),
            {
                'rbc': 3,
                'wbc': 5,
                'plt': 150,
                'p_neut': 10,
                'p_lymp': 10,
                'p_mono': 10,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'POSITIVE', response.content)

    def test_not_enough_hemogram_fields(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.post(
            reverse("rest-api:classify"),
            {
                'rbc': 3,
                'wbc': 5,
                'plt': 150,
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'hemogram result fields must be', response.content)

    def test_no_wbc_with_percentage_fields(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.post(
            reverse("rest-api:classify"),
            {
                'rbc': 3,
                'plt': 150,
                'mcv': 80,
                'mchc': 330,
                'neut': 0.1,
                'lymp': 0.1,
                'p_mono': 0.1,
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'WBC must be present', response.content)
