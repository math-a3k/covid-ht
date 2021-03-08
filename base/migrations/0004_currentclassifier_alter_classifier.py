# Generated by Django 3.1.5 on 2021-02-09 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supervised_learning', '0001_initial'),
        ('base', '0003_external_classifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currentclassifier',
            name='classifier',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='current_classifier', to='supervised_learning.supervisedlearningtechnique'),
        ),
    ]