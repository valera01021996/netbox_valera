from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from dcim.models import Region, Device
from tenancy.models import Tenant


class APKService(NetBoxModel):
    """Уровень 1 — верхний сервис (например, HSI, DRS)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "APK Service"
        verbose_name_plural = "APK Services"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:apk:apkservice", args=[self.pk])


class APKType(NetBoxModel):
    """Уровень 2 — подтип сервиса (например, PPPoE, Radius, Netflow)."""
    service = models.ForeignKey(APKService, on_delete=models.CASCADE, related_name="types")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "APK Type"
        verbose_name_plural = "APK Types"
        unique_together = ("service", "name")
        ordering = ["service", "name"]

    def __str__(self):
        return f"{self.service.name} → {self.name}"

    def get_absolute_url(self):
        return reverse("plugins:apk:apktype", args=[self.pk])

