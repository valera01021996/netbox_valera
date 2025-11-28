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


class APKRubejForm(NetBoxModelForm):
    class Meta:
        model = APK
        fields = (
            'type', 'operator', 'region', 'contract',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # При создании нового объекта автоматически устанавливаем type='Rubej'
        if not self.instance.pk:
            self.fields['type'].initial = 'Rubej'
            self.instance.type = 'Rubej'
        else:
            # При редактировании также принудительно устанавливаем Rubej
            self.instance.type = 'Rubej'
        
        # Скрываем поля, которые не нужны для Rubej
        fields_to_hide = ['name', 'ttx', 'port_type', 'ports_count', 'capacity', 'avg_traffic', 'retention_period']
        for field_name in fields_to_hide:
            if field_name in self.fields:
                del self.fields[field_name]

    def clean_type(self):
        # Принудительно устанавливаем type='Rubej' для объектов Rubej
        return 'Rubej'

    def save(self, commit=True):
        # Убеждаемся, что type='Rubej' перед сохранением
        instance = super().save(commit=False)
        instance.type = 'Rubej'
        if commit:
            instance.save()
        return instance
    