from django.urls import reverse
from netbox.models import NetBoxModel
from dcim.models import Device
from django.db import models

class DeviceScan(NetBoxModel):
    STATUS_CHOICES = [
        ("PENDING", "PENDING"),
        ("RUNNING", "RUNNING"),
        ("OK", "OK"),
        ("ERROR", "ERROR"),
    ]

    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="scan_status")
    last_started = models.DateTimeField(null=True, blank=True)
    last_finished = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    attemts = models.IntegerField(default=0)
    error = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.device} - {self.status}"

    def get_absolute_url(self):
        return reverse("plugins:device_scan:devicescan_view", args=[self.pk])


