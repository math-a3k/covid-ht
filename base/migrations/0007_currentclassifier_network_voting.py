# Generated by Django 3.1.5 on 2021-03-15 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_networknode'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentclassifier',
            name='network_voting',
            field=models.PositiveSmallIntegerField(choices=[(0, 'No Network Voting'), (1, 'Majority'), (2, 'Minimum of Postives'), (3, 'Minimum of Negatives')], default=0, verbose_name='Network Voting Policy'),
        ),
        migrations.AddField(
            model_name='currentclassifier',
            name='network_voting_threshold',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Only applicable for Minimum Positives / Negatives voting policies.', null=True, verbose_name='Network Voting Threshold'),
        ),
    ]