# Generated by Django 3.2.8 on 2021-12-15 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_alter_ids_bigautofield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalclassifier',
            name='timeout',
            field=models.PositiveSmallIntegerField(default=10, help_text='Seconds to wait for a response from the service', verbose_name='Request Timeout (s)'),
        ),
    ]
