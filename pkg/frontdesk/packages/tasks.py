from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.utils import timezone

from .models import Package


@shared_task
def fetch_package_status(package_id):
    # retrieve the package
    package = Package.objects.get(id=package_id)

    # TODO: query the carrier for the package status and update the model

    # update the last checked timestamp and save the package
    package.checked = timezone.now()
    package.save()
