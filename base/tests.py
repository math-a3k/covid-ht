from copy import deepcopy
import numpy as np
import random
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.test import Client, SimpleTestCase

from rest_framework.test import RequestsClient

from data.utils import trunc_normal
from data.models import Data
from units.models import Unit

from .models import (CurrentClassifier, DecisionTree, ExternalClassifier,
                     NetworkNode, User,)
from .utils import classification_tuple, get_current_classifier


class TestBase(SimpleTestCase):
    databases = "__all__"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        # Set the seeds
        random.seed(123456)
        np.random.seed(123456)
        #
        cls.classifier, _ = DecisionTree.objects.get_or_create(
            name="HGBTree for tests",
            data_model="data.Data",
            learning_target="is_covid19",
            cv_is_enabled=True,
            cv_folds=2,
            cv_metrics="accuracy",
            max_iter=10,
            random_state=123456
        )
        cls.classifier_external, _ = ExternalClassifier.objects.get_or_create(
            name="Local REST API Classifier for tests",
            service_url="http://localhost",
            endpoint_classify="/api/v1/classify",
            timeout=5,
        )
        cls.current_classifier, _ = CurrentClassifier.objects.get_or_create(
            classifier=cls.classifier,
        )
        cls.unit, _ = Unit.objects.get_or_create(
            name="Unit for tests"
        )
        cls.user, _ = User.objects.get_or_create(
            username='testuser',
            first_name='Test',
            last_name='User',
            user_type=User.MANAGER,
            unit=cls.unit,
            is_superuser=True,
            is_staff=True
        )
        cls.user.set_password("12345")
        cls.user.save()
        cls.node_1, _ = NetworkNode.objects.get_or_create(
            name='Node for Tests 1',
            classification_request=True
        )
        cls.node_2, _ = NetworkNode.objects.get_or_create(
            name='Node for Tests 2',
            classification_request=True
        )
        # Populate with data
        covid_size = 60
        no_covid_size = 40
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
                    user=cls.user,
                    unit=cls.unit,
                    is_covid19=is_covid19[i],
                    is_diabetic=is_diab,
                    rbc=rbc[i],
                    wbc=wbc[i],
                )
            )
        Data.objects.bulk_create(ds)
        cls.classifier.perform_inference()

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
        self.current_classifier.external = self.classifier_external
        self.current_classifier.classifier = self.classifier
        self.current_classifier.save()

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
        self.assertContains(response, 'Local REST API Classifier for tests')
        self.assertContains(response, 'POSITIVE')
        self.current_classifier.classifier = self.classifier
        self.current_classifier.external = None
        self.current_classifier.save()

    def test_classification_external_unavailable(self):
        self.current_classifier.external = self.classifier_external
        self.current_classifier.internal = None
        self.current_classifier.save()
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
        self.current_classifier.classifier = self.classifier
        self.current_classifier.external = None
        self.current_classifier.save()
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

    def test_network_classification(self):
        cc = deepcopy(self.current_classifier)
        drf_request_client = RequestsClient()
        observation = {
            'rbc': 3,
            'wbc': 5,
            'plt': 150,
            'neut': 0.5,
            'lymp_Upercentage_Rwbc': 10,
            'mono_Upercentage_Rwbc': 10,
        }
        # -> Test _get_network_votes()
        votes = cc._get_network_votes(observation)
        expected_result = {
            "local": {"result": "POSITIVE", "prob": 0.5685905603904713}
        }
        self.assertEqual(votes, expected_result)
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            votes = cc._get_network_votes(observation)
            expected_result = {
                'local': {'result': 'POSITIVE', 'prob': 0.5685905603904713},
                'Node for Tests 1': {
                    'result': 'POSITIVE', 'prob': 0.5685905603904713},
                'Node for Tests 2': {
                    'result': 'POSITIVE', 'prob': 0.5685905603904713}
            }
            self.assertEqual(votes, expected_result)

        # -> Test network_predict()
        cc.network_voting = cc.NETWORK_VOTING_MAJORITY
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "POSITIVE")
            self.assertEqual(s1, 0.5685905603904713)

        votes_patch = {
            'local': {'result': 'POSITIVE', 'prob': 0.5685905603904713},
            'Node for Tests 1': {'result': 'NEGATIVE', 'prob': 0.9},
            'Node for Tests 2': {'result': 'NEGATIVE', 'prob': 0.7}
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "NEGATIVE")
            self.assertEqual(s1, 0.8)

        votes_patch = {
            'local': {'result': 'POSITIVE', 'prob': 0.56},
            'Node for Tests 1': {'result': 'NEGATIVE', 'prob': 0.9},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "POSITIVE")
            self.assertEqual(s1, 0.56)

        votes_patch = {
            'local': {'result': 'NEGATIVE', 'prob': 0.56},
            'Node for Tests 1': {'result': 'POSITIVE', 'prob': 0.9},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "NEGATIVE")
            self.assertEqual(s1, 0.56)

        cc.network_voting = cc.NETWORK_VOTING_MIN_NEGATIVE
        cc.network_voting_threshold = 1
        votes_patch = {
            'local': {'result': 'NEGATIVE', 'prob': 0.56},
            'Node for Tests 1': {'result': 'POSITIVE', 'prob': 0.9},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "NEGATIVE")
            self.assertEqual(s1, 0.56)

        votes_patch = {
            'local': {'result': 'POSITIVE', 'prob': 0.7},
            'Node for Tests 1': {'result': 'POSITIVE', 'prob': 0.9},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "POSITIVE")
            self.assertEqual(s1, 0.8)

        cc.network_voting = cc.NETWORK_VOTING_MIN_POSITIVE
        cc.network_voting_threshold = 1
        votes_patch = {
            'local': {'result': 'NEGATIVE', 'prob': 0.56},
            'Node for Tests 1': {'result': 'POSITIVE', 'prob': 0.9},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "POSITIVE")
            self.assertEqual(s1, 0.9)

        votes_patch = {
            'local': {'result': 'NEGATIVE', 'prob': 0.7},
            'Node for Tests 1': {'result': 'NEGATIVE', 'prob': 0.9},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "NEGATIVE")
            self.assertEqual(s1, 0.8)

        cc.network_voting = cc.NETWORK_VOTING_DISABLED
        self.assertEqual(cc.network_predict(observation), None)

        # -> Test with local external classifier
        cc.external = self.classifier_external
        cc.network_voting = cc.NETWORK_VOTING_MAJORITY
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            with patch.object(ExternalClassifier,
                              '_requests_client', drf_request_client):
                p1, s1 = cc.network_predict(observation)
                self.assertEqual(p1, "POSITIVE")
                self.assertEqual(s1, 0.5685905603904713)

        # -> Test with local internal classifier not inferred
        cc.external = None
        cc.classifier.is_inferred = False
        cc.network_voting = cc.NETWORK_VOTING_MAJORITY
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            p1, s1 = cc.network_predict(observation)
            self.assertEqual(p1, "POSITIVE")
            self.assertEqual(s1, 0.5685905603904713)

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

    def test_currentclassifier_admin(self):
        self.client.login(username=self.user.username, password="12345")
        response = self.client.get(
            reverse(
                "admin:base_currentclassifier_change",
                args=(self.current_classifier.pk, ))
        )
        self.assertContains(response, "Node for Tests 1")
        self.assertContains(response, "Node for Tests 2")

    def test_rest_api_no_current_classifier(self):
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

    def test_rest_api_no_inference(self):
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

    def test_rest_api_classification(self):
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

    def test_rest_api_classification_with_percentage_fields(self):
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

    def test_rest_api_not_enough_hemogram_fields(self):
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

    def test_rest_api_no_wbc_with_percentage_fields(self):
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
