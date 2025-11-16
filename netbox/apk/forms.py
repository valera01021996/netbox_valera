from netbox.forms import NetBoxModelForm
from .models import APK

class APKForm(NetBoxModelForm):
    class Meta:
        model = APK
        fields = (
            'name', 'type', 'operator', 'region', 'contract',
            'ttx', 'port_type', 'ports_count', 'capacity',
            'avg_traffic', 'retention_period',
        )