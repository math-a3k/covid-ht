#
import random
import numpy as np
import uuid

from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from django_ai.ai_base.models import DataColumn
from django_ai.supervised_learning.models.hgb import HGBTree

from base.models import (User, CurrentClassifier)
from units.models import Unit

from .utils import trunc_normal
from .models import Data


class TestData(StaticLiveServerTestCase):
    """
    IMPORTANT NOTE: Still haven't found a way to trigger the run of the
    migrations of ai_base and supervised_learning (django-ai apps) for the
    test database.

    Without them, it is impossible to do automatic testing.
    """
    user = None
    unit = None

    def setUp(self):
        # Set the seeds
        random.seed(123456)
        np.random.seed(123456)
        #
        # print("Calling 'migrate' on ai_base and supervised_learning")
        # call_command('migrate', 'ai_base', verbosity=1)
        # call_command('migrate', 'supervised_learning', verbosity=1)
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
                    uuid=uuid.uuid4(),
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
