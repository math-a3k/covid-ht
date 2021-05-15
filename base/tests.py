from copy import deepcopy
from decimal import Decimal
import numpy as np
import random
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.test import Client, SimpleTestCase

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.test import RequestsClient

from data.utils import trunc_normal
from data.models import Data
from units.models import Unit

from .models import (CurrentClassifier, DecisionTree, ExternalClassifier,
                     NetworkErrorLog, NetworkNode, User,)


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
        cls.unit_node, _ = Unit.objects.get_or_create(
            name="Node Unit for tests"
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
        cls.user_node, _ = User.objects.get_or_create(
            username='testuser_node',
            first_name='Test',
            last_name='Node User',
            user_type=User.MANAGER,
            unit=cls.unit_node,
        )
        cls.user_node.set_password("12345")
        cls.user_node.save()
        cls.user_node_token = Token.objects.create(user=cls.user_node)
        cls.node_1, _ = NetworkNode.objects.get_or_create(
            name='Node for Tests 1',
            unit=cls.unit_node, user=cls.user_node,
            remote_user=cls.user_node.username,
            remote_user_token=cls.user_node_token.key,
            classification_request=True,
            data_sharing_is_enabled=False,
            metrics="accuracy_score"
        )
        cls.node_2, _ = NetworkNode.objects.get_or_create(
            name='Node for Tests 2',
            classification_request=True,
            data_sharing_is_enabled=False
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
        hgb = \
            list(np.floor(trunc_normal(80, 240, 140, 5, covid_size))) + \
            list(np.floor(trunc_normal(80, 240, 140, 5, no_covid_size)))
        hct = \
            trunc_normal(0.2, 0.8, 0.4, 0.2, table_size)
        mcv = \
            list(np.floor(trunc_normal(60, 150, 80, 10, covid_size))) + \
            list(np.floor(trunc_normal(60, 150, 80, 10, no_covid_size)))
        mchc = \
            list(trunc_normal(2, 5, 3, 1, table_size))
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
                    hgb=hgb[i],
                    hct=hct[i],
                    mcv=mcv[i],
                    mchc=mchc[i],
                    is_finished=True
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

        post_patch = Response(
            {"result": "POSITIVE", "prob": 0.888}, status=200
        )
        post_patch.json = lambda: {"result": ["POSITIVE"], "prob": [0.888]}

        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            with patch.object(ExternalClassifier._requests_client,
                              'post',
                              return_value=post_patch):
                data = {
                    'rbc': 3,
                    'wbc': 5,
                    'plt': 150,
                    'neut': 0.1,
                    'lymp': 0.1,
                    'mono': 0.1,
                }
                response = self.client.post(reverse("base:home"), data=data)
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

        data = {
           'rbc': 3,
           'wbc': 5,
           'plt': 150,
           'neut': 0.1,
           'lymp': 0.1,
           'mono': 0.1,
        }

        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            with patch.object(CurrentClassifier.objects, 'last',
                              return_value=None):
                response = self.client.post(reverse("base:home"), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classification Service Unavailable')

        # -> Test with Network Unreachable
        response = self.client.post(reverse("base:home"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classification Service Unavailable')

        # -> Test other errors
        post_patch = Response({"detail": "does-not-exists"}, status=404)
        post_patch.content = b'{"detail": "does-not-exists"}'
        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            with patch.object(ExternalClassifier._requests_client,
                              'post',
                              return_value=post_patch):
                response = self.client.post(reverse("base:home"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Classification Service Unavailable')

        self.current_classifier.classifier = self.classifier
        self.current_classifier.external = None
        self.current_classifier.save()

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
            'local ({})'.format(settings.CHTUID):
                {"result": ["POSITIVE"], "prob": [0.6300912038351191]}
        }
        self.assertEqual(votes, expected_result)
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            cc.network_voting = cc.NETWORK_VOTING_MAJORITY
            self.node_1.metadata = {}
            self.node_1.save()
            self.node_2.metadata = {}
            self.node_2.save()
            votes = cc._get_network_votes(observation)
            expected_result = {
                'local ({})'.format(settings.CHTUID):
                    {'result': ['POSITIVE'], 'prob': [0.6300912038351191]},
                'Node for Tests 1 (-)': {
                    'result': ['POSITIVE'], 'prob': [0.6300912038351191]},
                'Node for Tests 2 (-)': {
                    'result': ['POSITIVE'], 'prob': [0.6300912038351191]}
            }
            self.assertEqual(votes, expected_result)

        # -> Test network_predict()
        cc.network_voting = cc.NETWORK_VOTING_MAJORITY
        p1, s1, v1 = cc.network_predict([observation])
        self.assertEqual(p1, ["POSITIVE"])
        self.assertEqual(s1, [0.6300912038351191])
        self.assertEqual(v1, {
            'local ({})'.format(settings.CHTUID):
                {"result": ["POSITIVE"], "prob": [0.6300912038351191]}
        })

        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            p1, s1, v1 = cc.network_predict([observation])
            self.assertEqual(p1, ["POSITIVE"])
            self.assertEqual(s1, [0.6300912038351191])

        votes_patch = {
            'local': {'result': ['POSITIVE'], 'prob': [0.6300912038351191]},
            'Node for Tests 1': {'result': ['NEGATIVE'], 'prob': [0.9]},
            'Node for Tests 2': {'result': ['NEGATIVE'], 'prob': [0.7]}
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1, v1 = cc.network_predict(observation)
            self.assertEqual(p1, ["NEGATIVE"])
            self.assertEqual(s1, [0.8])

        votes_patch = {
            'local': {'result': ['POSITIVE'], 'prob': [0.56]},
            'Node for Tests 1': {'result': ['NEGATIVE'], 'prob': [0.9]},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation, include_votes=False)
            self.assertEqual(p1, ["POSITIVE"])
            self.assertEqual(s1, [0.56])

        votes_patch = {
            'local': {'result': ['NEGATIVE'], 'prob': [0.56]},
            'Node for Tests 1': {'result': ['POSITIVE'], 'prob': [0.9]},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation, include_votes=False)
            self.assertEqual(p1, ["NEGATIVE"])
            self.assertEqual(s1, [0.56])

        cc.breaking_ties_policy = cc.BTP_SCORES
        votes_patch = {
            'local': {'result': ['POSITIVE'], 'prob': [0.56]},
            'Node for Tests 1': {'result': ['NEGATIVE'], 'prob': [0.9]},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation, include_votes=False)
            self.assertEqual(p1, ["NEGATIVE"])
            self.assertEqual(s1, [0.9])

        votes_patch = {
            'local': {'result': ['NEGATIVE'], 'prob': [0.56]},
            'Node for Tests 1': {'result': ['POSITIVE'], 'prob': [0.9]},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation, include_votes=False)
            self.assertEqual(p1, ["POSITIVE"])
            self.assertEqual(s1, [0.9])

        cc.network_voting = cc.NETWORK_VOTING_MIN_NEGATIVE
        cc.network_voting_threshold = 1
        votes_patch = {
            'local': {'result': ['NEGATIVE'], 'prob': [0.56]},
            'Node for Tests 1': {'result': ['POSITIVE'], 'prob': [0.9]},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation, include_votes=False)
            self.assertEqual(p1, ["NEGATIVE"])
            self.assertEqual(s1, [0.56])

        votes_patch = {
            'local': {'result': ['POSITIVE'], 'prob': [0.7]},
            'Node for Tests 1': {'result': ['POSITIVE'], 'prob': [0.9]},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation, include_votes=False)
            self.assertEqual(p1, ["POSITIVE"])
            self.assertEqual(s1, [0.8])

        cc.network_voting = cc.NETWORK_VOTING_MIN_POSITIVE
        cc.network_voting_threshold = 1
        votes_patch = {
            'local': {'result': ['NEGATIVE'], 'prob': [0.56]},
            'Node for Tests 1': {'result': ['POSITIVE'], 'prob': [0.9]},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation, include_votes=False)
            self.assertEqual(p1, ["POSITIVE"])
            self.assertEqual(s1, [0.9])

        votes_patch = {
            'local': {'result': ['NEGATIVE'], 'prob': [0.7]},
            'Node for Tests 1': {'result': ['NEGATIVE'], 'prob': [0.9]},
        }
        with patch.object(CurrentClassifier,
                          '_get_network_votes', return_value=votes_patch):
            p1, s1 = cc.network_predict(observation, include_votes=False)
            self.assertEqual(p1, ["NEGATIVE"])
            self.assertEqual(s1, [0.8])

        # cc.network_voting = cc.NETWORK_VOTING_DISABLED
        # self.assertEqual(cc.network_predict(observation), None)

        # -> Test with local external classifier
        cc.external = self.classifier_external
        cc.network_voting = cc.NETWORK_VOTING_MAJORITY
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            with patch.object(ExternalClassifier,
                              '_requests_client', drf_request_client):
                p1, s1, v1 = cc.network_predict(observation)
                self.assertEqual(p1, ["POSITIVE"])
                self.assertEqual(s1, [0.6300912038351191])

        # -> Test with local internal classifier not inferred
        cc.external = None
        cc.classifier.is_inferred = False
        cc.network_voting = cc.NETWORK_VOTING_MAJORITY
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            p1, s1, v1 = cc.network_predict(observation)
            self.assertEqual(p1, ["POSITIVE"])
            self.assertEqual(s1, [0.6300912038351191])

    def test_network_data_sharing(self):
        self.node_1.data_sharing_is_enabled = True
        self.node_1.save()
        NetworkErrorLog.objects.all().delete()
        self.client.force_login(user=self.user)
        drf_request_client = RequestsClient()

        post_data = {
            'unit_ii': "test_network_data_sharing",
            'is_covid19': True,
            'rbc': Decimal("3"),
            'wbc': Decimal("5"),
            'plt': Decimal("150"),
            'neut': Decimal("0.1"),
            'lymp': Decimal("0.1"),
            'mono': Decimal("0.1"),
        }
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            response = self.client.post(
                reverse("data:input"),
                post_data,
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        # If no error logs were generated, the requests were sent
        # and were successful, endpoints are tested in data.tests
        self.assertEqual(list(NetworkErrorLog.objects.all()), [])

        self.node_1.data_sharing_mode = \
            self.node_1.DATA_SHARING_MODE_ON_FINISHED
        self.node_1.save()

        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            response = self.client.post(
                reverse("data:input"),
                post_data,
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(NetworkErrorLog.objects.all()), [])

        post_data["is_finished"] = True
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            response = self.client.post(
                reverse("data:input"),
                post_data,
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(NetworkErrorLog.objects.all()), [])

        # -> Test Error Logs catching errors
        response = self.client.post(
                reverse("data:input"),
                post_data,
                follow=True
            )
        # Data is created
        self.assertEqual(response.status_code, 200)
        # but not propagated
        error_log = NetworkErrorLog.objects.last()
        self.assertIn('[Errno 111] Connection refused', error_log.message)

        self.node_1.remote_user_token = None
        self.node_1.save()
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            response = self.client.post(
                reverse("data:input"),
                post_data,
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        error_log = NetworkErrorLog.objects.last()
        self.assertEqual(403, error_log.status_code)

        self.node_1.data_sharing_is_enabled = False
        self.node_1.remote_user_token = self.user_node_token.key
        self.node_1.save()

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
        self.client.force_login(user=self.user)
        response = self.client.get(
            reverse(
                "admin:base_currentclassifier_change",
                args=(self.current_classifier.pk, ))
        )
        self.assertContains(response, "Node for Tests 1")
        self.assertContains(response, "Node for Tests 2")

    def test_networknode_share_data(self):
        drf_request_client = RequestsClient()
        with patch.object(NetworkNode,
                          '_requests_client', drf_request_client):
            success = self.node_1.share_data({
                'is_finished': False,
                'rbc': 3,
                'plt': 150,
                'mcv': 80,
                'wbc': 3,
                'neut': 0.1,
                'lymp': 0.1,
            })
        self.assertEqual(success, True)

    def test_update_metadata_view(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        self.client.force_login(user=self.user)
        drf_request_client = RequestsClient()
        self.node_1.metadata = {}
        self.node_1.save()
        self.assertEqual(self.node_1.metadata, {})
        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            response = self.client.get(
                reverse("base:update_metadata",
                        args=[self.node_1.externalclassifier_ptr_id, ]),
            )
        self.assertEqual(response.status_code, 302)
        self.node_1.refresh_from_db()
        self.assertNotEqual(self.node_1.metadata, {})
        # Test no update
        self.node_1.metadata = {}
        self.node_1.save()
        response = self.client.get(
                reverse("base:update_metadata",
                        args=[self.node_1.externalclassifier_ptr_id, ]),
            )
        self.assertEqual(response.status_code, 302)
        self.node_1.refresh_from_db()
        self.assertEqual(self.node_1.metadata, {})
        error_log = NetworkErrorLog.objects.last()
        self.assertIn('[Errno 111] Connection refused', error_log.message)

    def test_networknode_eval_metrics(self):
        self.client.force_login(user=self.user)
        drf_request_client = RequestsClient()
        self.node_1.metadata = {}
        self.node_1.save()
        # Test with no CurrentClassifier
        CurrentClassifier.objects.last().delete()
        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            scores = self.node_1.eval_metrics()
        self.assertEqual(scores, False)
        # Test with no network access
        scores = self.node_1.eval_metrics()
        self.assertEqual(scores, False)
        # Test with no metrics
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        self.node_1.metrics = None
        self.node_1.save()
        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            scores = self.node_1.eval_metrics()
        self.assertEqual(scores, {})
        self.node_1.metrics = "accuracy_score"
        self.node_1.save()

    def test_externalclassifier_update_metadata(self):
        self.client.force_login(user=self.user)
        drf_request_client = RequestsClient()
        self.assertEqual(self.node_1.metadata, {})
        # Test with no CurrentClassifier
        CurrentClassifier.objects.last().delete()
        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            metadata = self.node_1.update_metadata(save=False)
        self.assertEqual(metadata, False)
        # Test with no network access
        metadata = self.node_1.update_metadata()
        self.assertEqual(metadata, False)
        # Test with no metrics
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        self.node_1.metrics = None
        self.node_1.save()
        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            metadata = self.node_1.update_metadata(save=False)
        self.assertEqual("scores" not in metadata["local_data"], True)
        self.node_1.metrics = "accuracy_score"
        self.node_1.save()
        # Test with eval_metrics errors
        with patch.object(ExternalClassifier,
                          '_requests_client', drf_request_client):
            with patch.object(NetworkNode,
                              'eval_metrics', return_value=False):
                metadata = self.node_1.update_metadata(save=False)
        self.assertEqual(metadata, False)

    def test_networknode_clean(self):
        self.node_1.clean()
        self.node_1.metrics = None
        self.node_1.clean()
        self.node_1.metrics = "unrecognized_metrics"
        with self.assertRaises(ValidationError):
            self.node_1.clean()
        self.node_1.metrics = "accuracy_score"

    def test_covidhtmixin(self):
        self.classifier.perform_inference(save=False)
        self.assertTrue(
            self.classifier
            .metadata["inference"]["current"]["conf"]["timestamp"] is not None
        )

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

        response = self.client.post(
            reverse("rest-api:classify") + '?use_network=True',
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
        self.assertIn(b'votes', response.content)

    def test_rest_api_metadata(self):
        cc, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        response = self.client.get(reverse("rest-api:classify"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'inference', response.content)
        # Test unavailable
        cc.delete()
        response = self.client.get(reverse("rest-api:classify"))
        self.assertEqual(response.status_code, 503)

    def test_rest_api_dataset_classification(self):
        _, _ = CurrentClassifier.objects.get_or_create(
            classifier=self.classifier
        )
        self.classifier.perform_inference()
        expected_result = {
            "result": ["POSITIVE", "POSITIVE"],
            "prob": [0.8321382707460566, 0.8321382707460566]
        }
        response = self.client.post(
            reverse("rest-api:classify-dataset"),
            {"dataset": [
                    {
                        "rbc": 3, "wbc": 5, "plt": 150,
                        "neut": 0.3, "lymp": 0.3, "mono": 0.3
                    },
                    {
                        "rbc": 3, "wbc": 5, "plt": 150,
                        "neut_Upercentage_Rwbc": 10,
                        "lymp_Upercentage_Rwbc": 10,
                        "mono_Upercentage_Rwbc": 10
                    },
               ]
             },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_result, response.json())

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
