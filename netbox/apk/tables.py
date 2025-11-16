from netbox.tables import NetBoxTable
import django_tables2 as tables
from django.utils.html import format_html
from .models import APK

class APKTable(NetBoxTable):
    devices = tables.Column(verbose_name=('Devices'), empty_values=())
    class Meta(NetBoxTable.Meta):
        model = APK
        fields = ('pk', 'id', 'name', 'type', 'operator', 'region', 'contract', 'ttx', 'port_type', 'ports_count', 'capacity', 'avg_traffic', 'retention_period')
        default_columns = ('name', 'type', 'operator', 'region', 'contract', 'ttx', 'port_type', 'ports_count', 'capacity', 'avg_traffic', 'retention_period')

    def render_devices(self, record):
        count = record.get_devices().count()
        if count == 0:
            return '—'
        return format_html('<a href="{}">{}</a>', record.get_device_filter_url(), count)