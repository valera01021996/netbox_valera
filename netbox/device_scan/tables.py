import django_tables2 as tables
from netbox.tables import NetBoxTable
from .models import DeviceScan

class DeviceScanTable(NetBoxTable):
    device = tables.Column(
        linkify=lambda record: record.device.get_absolute_url()
    )
    status = tables.Column()
    last_started = tables.DateTimeColumn()
    last_finished = tables.DateTimeColumn()
    attemts = tables.Column()
    error = tables.Column()


    class Meta(NetBoxTable.Meta):
        model = DeviceScan
        fields = ('device', 'status', 'last_started', 'last_finished', 'attemts', 'error')
        default_columns = ('device', 'status', 'last_finished', 'error')
        