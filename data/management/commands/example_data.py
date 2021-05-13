import random
import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token
from django_ai.supervised_learning.models import SupervisedLearningTechnique

from base.models import CurrentClassifier, DecisionTree, SVM, User
from data.models import Data
from data.utils import get_hemogram_data
from units.models import Unit


random.seed(123456)


class Command(BaseCommand):
    help = 'Create, reset and remove example data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resets example data observations (Data Model)',
        )

        parser.add_argument(
            '--remove',
            action='store_true',
            help='Removes example data (observations, units, users)',
        )

        parser.add_argument(
            '--create',
            action='store_true',
            help='Creates EXAMPLE_DATA_SIZE observations (along with Units, '
            'Users and Techniques if needed)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            data = Data.objects.filter(unit__name__icontains="(E)").delete()
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully reseted example data ({} observations)'
                    .format(data[0])
                )
            )

        if options['remove']:
            cc = CurrentClassifier.objects.last()
            if cc:
                if "(Example)" in cc.classifier.name:
                    cc.delete()
            Data.objects.filter(unit__name__icontains="(E)").delete()
            User.objects.filter(last_name__icontains="(E)").delete()
            Unit.objects.filter(name__icontains="(E)").delete()
            SupervisedLearningTechnique.objects\
                .filter(name__icontains="(Example)").delete()

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully removed example data (observations, '
                    'users, units and techniques)'
                )
            )

        if options['create']:
            # Get or Create Units
            unit1, _ = Unit.objects.get_or_create(
                name="Lab at Hospital A (E)"
            )
            Unit.objects.get_or_create(
                name="Lab at Hospital B (E)"
            )
            Unit.objects.get_or_create(
                name="Local Lab C (E)"
            )
            Unit.objects.get_or_create(
                name="Clinic D (E)"
            )
            unit5, _ = Unit.objects.get_or_create(
                name="Healthcare Facility E (E)"
            )
            # Get or Create Users
            u_manager = User.objects.get_or_create(
                username='manager',
                defaults={
                    'first_name': 'Manager',
                    'last_name': 'Rodríguez (E)',
                    'unit': unit5,
                    'email': 'mrodriguez@example.com',
                    'cellphone': "123 123 123",
                    'user_type': User.MANAGER
                }
            ),
            u_staff = User.objects.get_or_create(
                username='staff',
                defaults={
                    'first_name': 'Estaff',
                    'last_name': 'García (E)',
                    'is_staff': True,
                    'unit': unit5
                }
            )
            users = [u_manager[0][0], u_staff[0]]
            users[0].set_password('manager')
            users[0].save()
            users[1].set_password('staff')
            users[1].save()
            # Assign Permissions
            hgb_ct = ContentType.objects.get_for_model(DecisionTree)
            svm_ct = ContentType.objects.get_for_model(SVM)
            cc_ct = ContentType.objects.get_for_model(CurrentClassifier)
            p1 = Permission.objects.get(
                content_type=hgb_ct, codename="add_decisiontree"
            )
            p2 = Permission.objects.get(
                content_type=hgb_ct, codename="change_decisiontree"
            )
            p3 = Permission.objects.get(
                content_type=hgb_ct, codename="view_decisiontree"
            )
            p4 = Permission.objects.get(
                content_type=svm_ct, codename="add_svm"
            )
            p5 = Permission.objects.get(
                content_type=svm_ct, codename="change_svm"
            )
            p6 = Permission.objects.get(
                content_type=svm_ct, codename="view_svm"
            )
            users[1].user_permissions.add(p1, p2, p3, p4, p5, p6)
            p8 = Permission.objects.get(
                content_type=cc_ct, codename="change_currentclassifier"
            )
            p9 = Permission.objects.get(
                content_type=cc_ct, codename="view_currentclassifier"
            )
            users[1].user_permissions.add(p8, p9)
            # Get or Create Auth Token
            Token.objects.get_or_create(
                user=u_staff[0],
                defaults={
                    "key": "TheQuickBrownFox..."
                }
            )
            # Get or Create Classification Techniques
            SVM.objects.get_or_create(
                name="SVC 1 (Example)",
                defaults={
                    'data_model': "data.Data",
                    'learning_target': "is_covid19",
                    'data_imputer': ("django_ai.supervised_learning.models."
                                     "IntrospectionImputer"),
                    'cv_is_enabled': True,
                    'cv_folds': 10,
                    'cv_metrics': ("accuracy, precision, recall, "
                                   "fowlkes_mallows_score"),
                    'random_state': 123456
                }
            )
            hgb_1, _ = DecisionTree.objects.get_or_create(
                name="HGB 1 (Example)",
                defaults={
                    "data_model": "data.Data",
                    "learning_target": "is_covid19",
                    "cv_is_enabled": True,
                    "cv_folds": 10,
                    "cv_metrics": ("accuracy, precision, recall, "
                                   "fowlkes_mallows_score"),
                    "random_state": 123456
                }
            )
            DecisionTree.objects.get_or_create(
                name="HGB Scratchpad (Example)",
                data_model="data.Data",
                cv_is_enabled=True,
                cv_folds=10,
                cv_metrics=("accuracy, precision, recall, "
                            "fowlkes_mallows_score"),
                random_state=123456
            )
            cc = CurrentClassifier.objects.last()
            if not cc:
                CurrentClassifier.objects.create(
                    classifier=hgb_1.supervisedlearningtechnique
                )
            # Create Observations
            ds = []
            for i in range(0, settings.EXAMPLE_DATA_SIZE):
                u = random.sample(users, 1)[0]
                d = Data(
                        uuid=uuid.uuid4(),
                        user=u,
                        unit=u.unit,
                        **get_hemogram_data(for_input=True, is_finished=True)
                    )
                # Add some missing data
                d.is_diabetic = d.is_diabetic \
                    if random.random() > 0.1 else None
                d.is_hypertense = d.is_hypertense \
                    if random.random() > 0.1 else None
                d.is_with_other_conds = d.is_with_other_conds \
                    if random.random() > 0.1 else None
                ds.append(d)
            data = Data.objects.bulk_create(ds)

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created example data (%s observations)' % (
                        len(data),
                    )
                )
            )
