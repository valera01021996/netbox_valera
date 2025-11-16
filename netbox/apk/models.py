from django.db import models
from django.urls import reverse
from dcim.models import Device
from netbox.models import NetBoxModel


class APK(NetBoxModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    operator = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=255, blank=True)
    contract = models.CharField(max_length=255, blank=True)
    ttx = models.CharField(max_length=255, blank=True)
    port_type = models.CharField(max_length=255, blank=True)
    ports_count = models.CharField(max_length=255, blank=True, null=True)
    capacity = models.CharField(max_length=255, blank=True, null=True)
    avg_traffic = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    retention_period = models.CharField(max_length=255, blank=True)
    CUSTOMFIELD_SLUG = 'APK'

    def __str__(self) -> str:
        t = (self.type or '').strip()
        if t.lower() == "drs":
            return t or "DRS"
        elif t.lower() == "rubej":
            return t or "Rubej"
        else:
            # если name пустое, чтобы не было "APK  None"
            n = (self.name or '').strip()
            r = (self.region or '').strip()
            if n:
                return f"{n} {t} {r}".strip()
            return f"{t}" if t else "APK"


    def get_devices(self):
        return Device.objects.filter(**{f'custom_field_data__{self.CUSTOMFIELD_SLUG}': self.pk})

    def get_device_filter_url(self):
        return f"{reverse('dcim:device_list')}?cf_{self.CUSTOMFIELD_SLUG}={self.pk}"

    

