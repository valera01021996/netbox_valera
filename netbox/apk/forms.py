from netbox.forms import NetBoxModelForm
from .models import APK


class APKForm(NetBoxModelForm):
    class Meta:
        model = APK
        fields = (
            'name', 'type', 'operator', 'region', 'contract',
            'ttx', 'port_type', 'ports_count', 'capacity',
        )


class APKDRSForm(NetBoxModelForm):
    class Meta:
        model = APK
        fields = (
            'name', 'type', 'operator', 'region', 'contract',
            'avg_traffic', 'retention_period',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # При создании нового объекта автоматически устанавливаем type='DRS'
        if not self.instance.pk:
            self.fields['type'].initial = 'DRS'
            # Устанавливаем значение напрямую в instance
            self.instance.type = 'DRS'
        else:
            # При редактировании также принудительно устанавливаем DRS
            self.instance.type = 'DRS'
        
        # Скрываем поля, которые не нужны для DRS
        fields_to_hide = ['ttx', 'port_type', 'ports_count', 'capacity']
        for field_name in fields_to_hide:
            if field_name in self.fields:
                del self.fields[field_name]

    def clean_type(self):
        # Принудительно устанавливаем type='DRS' для объектов DRS
        return 'DRS'

    def save(self, commit=True):
        # Убеждаемся, что type='DRS' перед сохранением
        instance = super().save(commit=False)
        instance.type = 'DRS'
        if commit:
            instance.save()
        return instance
    