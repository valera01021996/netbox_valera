from django.db import models
from netbox.models import NetBoxModel
from tenancy.models import Tenant
from django.urls import reverse
from dcim.models import Device

class APKName(NetBoxModel):
    name = models.CharField("Название АПК", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True)


    class Meta:
        verbose_name = "APK Name"
        verbose_name_plural = "APK Names"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:apk:apkname", args=[self.pk])


class APKEntry(NetBoxModel):
    apk_type = models.CharField("Тип АПК", max_length=100)
    apk_name = models.ForeignKey(APKName, on_delete=models.PROTECT, related_name="entries", verbose_name="APK Name")
    operator = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name="Оператор", related_name="apk_entries")
    contract = models.CharField("Договор", max_length=200, blank=True)
    ports_count = models.IntegerField("Кол-во портов", default=0)
    capacity_mbps = models.IntegerField("Ёмкость лицензии", default=0)
    ports_type = models.CharField(
        "Тип портов",
        max_length=20
    )
    specs = models.CharField("ТТХ", max_length=200)


    def devices_qs(self):
        return Device.objects.filter(
            custom_field_data__apk_name=self.apk_name_id,
            tenant_id=self.operator_id,
        )

    def devices_count(self):
        return self.devices_qs().count()


    class Meta:
        verbose_name = "APK Entry"
        verbose_name_plural = "APK Entries"
        ordering = ["apk_type", "apk_name", "operator"]

    def __str__(self):
        return f"{self.apk_name} ({self.apk_type})"

    def get_absolute_url(self):
        return reverse("plugins:apk:apkentry", args=[self.pk])



