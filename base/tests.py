#
import random
import numpy as np
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from rest_framework.test import (APITestCase, RequestsClient, )

from data.utils import trunc_normal
from data.models import Data
from units.models import Unit

from .models import CurrentClassifier, ExternalClassifier, User, DecisionTree
from .utils import classification_tuple, get_current_classifier


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
        self.classifier, _ = DecisionTree.objects.get_or_create(
            name="HGBTree for tests",
            data_model="data.Data",
            learning_target="is_covid19",
            cv_is_enabled=True,
            cv_folds=2,
            cv_metrics="accuracy",
            max_iter=10,
            random_state=123456
        )
        self.classifier_external, _ = ExternalClassifier.objects.get_or_create(
            name="Local REST API Classifier for tests",
            classifier_url="http://localhost/api/v1/classify",
            timeout=5,
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
        self.classifier.perform_inference()

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
        self.classifier.reset_inference()
        response = self.client.get(reverse("base:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No training has been done yet.")
        classifier = get_current_classifier()
        self.assertEqual(
            classification_tuple(classifier, []),
            (None, None)
        )

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

    def test_classification_external(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier, external=self.classifier_external
        )
        self.classifier.perform_inference()

        drf_request_client = RequestsClient()

        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
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

    def test_classification_external_unavailable(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier, external=self.classifier_external
        )
        self.classifier.perform_inference()

        drf_request_client = RequestsClient()

        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            with patch('base.v1.views.get_current_classifier',
                       return_value=None):
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
        self.assertContains(response, 'Classification Service Unavailable')

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
                'neut_Upercentage_Rwbc': 10,
                'lymp_Upercentage_Rwbc': 10,
                'mono_Upercentage_Rwbc': 10,
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
                'mono_Upercentage_Rwbc': 10,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class=" validate invalid" id="id_wbc">')

    def test_about(self):
        response = self.client.get(reverse("base:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About')

    def test_currentclassifier_no_internal_no_external(self):
        cc = CurrentClassifier()
        with self.assertRaises(ValidationError):
            cc.clean()

    def test_currentclassifier_clean(self):
        cc = CurrentClassifier()
        with self.assertRaises(ValidationError):
            cc.clean()
        cc.external = self.classifier_external
        cc.clean()


class TestBaseRESTAPI(APITestCase):

    def setUp(self):
        # Set the seeds
        random.seed(123456)
        np.random.seed(123456)
        #
        self.classifier, _ = DecisionTree.objects.get_or_create(
            name="HGBTree for API tests",
            data_model="data.Data",
            learning_target="is_covid19",
            cv_is_enabled=False,
            random_state=123456
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
        self.classifier.perform_inference()

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
        self.classifier.reset_inference()
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
                'neut_Upercentage_Rwbc': 10,
                'lymp_Upercentage_Rwbc': 10,
                'mono_Upercentage_Rwbc': 10,
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
                'mchc': 4,
                'neut': 0.1,
                'lymp': 0.1,
                'mono_Upercentage_Rwbc': 0.1,
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'"wbc":["This field must be present', response.content)
