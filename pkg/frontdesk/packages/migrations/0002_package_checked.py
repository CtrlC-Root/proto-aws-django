# Generated by Django 2.2 on 2019-07-24 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='checked',
            field=models.DateTimeField(blank=True, help_text='Retrieved package status from carrier.', null=True),
        ),
    ]
