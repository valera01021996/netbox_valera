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
    avg_traffic = models.CharField(max_length=255, blank=True, null=True)
    retention_period = models.CharField(max_length=255, blank=True, null=True)
    CUSTOMFIELD_SLUG = 'APK'

    def __str__(self) -> str:
        t = (self.type or '').strip()
        if t.lower() == "drs":
            r = (self.region or '').strip()
            o = (self.operator or '').strip()
            return f"{t} {r} {o}".strip()
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
        # Ищем устройства, связанные через общее поле APK
        return Device.objects.filter(**{f'custom_field_data__{self.CUSTOMFIELD_SLUG}': self.pk})

    def get_device_filter_url(self):
        # Используем общее поле APK для фильтрации
        return f"{reverse('dcim:device_list')}?cf_{self.CUSTOMFIELD_SLUG}={self.pk}"

    def get_absolute_url(self):
        # Определяем URL в зависимости от типа
        if self.type and self.type.lower() == 'drs':
            return reverse('plugins:apk:apk_drs', args=[self.pk])
        return reverse('plugins:apk:apk_hsi', args=[self.pk])

    @classmethod
    def _get_action_url(cls, action, rest_api=False, kwargs=None):
        """
        Переопределяет стандартное построение URL для модели APK.
        URL определяется динамически на основе типа объекта.
        """
        if kwargs is None:
            kwargs = {}
        
        # Если передан pk, проверяем тип объекта
        pk = kwargs.get('pk')
        is_drs = False
        if pk:
            try:
                obj = cls.objects.get(pk=pk)
                is_drs = obj.type and obj.type.lower() == 'drs'
            except cls.DoesNotExist:
                pass

        if rest_api:
            # Для REST API используем стандартный формат
            viewname = f'plugins-api:apk-api:apk'
            if action:
                viewname = f'{viewname}-{action}'
        else:
            # Для веб-интерфейса используем кастомные имена URL в зависимости от типа
            if is_drs:
                action_map = {
                    'list': 'plugins:apk:apk_drs_list',
                    'add': 'plugins:apk:apk_drs_add',
                    'edit': 'plugins:apk:apk_drs_edit',
                    'delete': 'plugins:apk:apk_drs_delete',
                    'changelog': 'plugins:apk:apk_drs_changelog',
                    'bulk_delete': 'plugins:apk:apk_drs_bulk_delete',
                }
                if action is None or action == '':
                    viewname = 'plugins:apk:apk_drs'
                else:
                    viewname = action_map.get(action)
                    if viewname is None:
                        viewname = f'plugins:apk:apk_drs_{action}'
            else:
                action_map = {
                    'list': 'plugins:apk:apk_hsi_list',
                    'add': 'plugins:apk:apk_hsi_add',
                    'edit': 'plugins:apk:apk_hsi_edit',
                    'delete': 'plugins:apk:apk_hsi_delete',
                    'changelog': 'plugins:apk:apk_hsi_changelog',
                    'bulk_delete': 'plugins:apk:apk_hsi_bulk_delete',
                }
                if action is None or action == '':
                    viewname = 'plugins:apk:apk_hsi'
                else:
                    viewname = action_map.get(action)
                    if viewname is None:
                        viewname = f'plugins:apk:apk_hsi_{action}'
        
        return reverse(viewname, kwargs=kwargs)
