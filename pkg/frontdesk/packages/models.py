import enum

from django.db import models
from django.utils import timezone


class Carrier(enum.Enum):
    USPS = "USPS"
    UPS = "UPS"
    FEDEX = "FedEx"


class Package(models.Model):
    """
    A package identified by the original shipping carrier and tracking number.
    """

    class Meta:
        ordering = ['-created']
        constraints = [
            models.UniqueConstraint(
                name='carrier_tracking_number',
                fields=['carrier', 'tracking_number'])
        ]

    carrier = models.CharField(
        max_length=16,
        choices=[(tag, tag.value) for tag in Carrier],
        help_text="Carrier that shipped the package.")

    tracking_number = models.CharField(
        max_length=64,
        help_text="Initial carrier tracking number.")

    created = models.DateTimeField(
        default=timezone.now,
        help_text="Tracking label created.")

    expected = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Estimated delivery date.")
