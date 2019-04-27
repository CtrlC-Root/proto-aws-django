# Generated by Django 2.2 on 2019-04-27 15:25

from django.db import migrations, models
import django.utils.timezone
import packages.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('carrier', models.CharField(
                    choices=[
                        (packages.models.Carrier('USPS'), 'USPS'),
                        (packages.models.Carrier('UPS'), 'UPS'),
                        (packages.models.Carrier('FedEx'), 'FedEx')],
                    help_text='Carrier that shipped the package.',
                    max_length=16)),
                ('tracking_number', models.CharField(
                    help_text='Initial carrier tracking number.',
                    max_length=64)),
                ('created', models.DateTimeField(
                    default=django.utils.timezone.now,
                    help_text='Tracking label created.')),
                ('expected', models.DateTimeField(
                    blank=True,
                    help_text='Estimated delivery date.',
                    null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.AddConstraint(
            model_name='package',
            constraint=models.UniqueConstraint(
                fields=('carrier', 'tracking_number'),
                name='carrier_tracking_number'),
        ),
    ]
