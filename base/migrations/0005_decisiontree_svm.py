# Generated by Django 3.1.5 on 2021-03-05 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supervised_learning', '0009_hgbtreeimputer'),
        ('base', '0004_currentclassifier_alter_classifier'),
    ]

    operations = [
        migrations.CreateModel(
            name='DecisionTree',
            fields=[
                ('hgbtreeclassifier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervised_learning.hgbtreeclassifier')),
            ],
            options={
                'abstract': False,
            },
            bases=('supervised_learning.hgbtreeclassifier',),
        ),
        migrations.CreateModel(
            name='SVM',
            fields=[
                ('svc_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supervised_learning.svc')),
            ],
            options={
                'abstract': False,
            },
            bases=('supervised_learning.svc',),
        ),
    ]
