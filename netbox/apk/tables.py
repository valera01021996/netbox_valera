import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import APKService


class APKServiceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    actions = columns.ActionsColumn(actions=('edit', 'delete'))

    class Meta(NetBoxTable.Meta):
        model = APKService
        fields = ('name', 'description', 'created')
        default_columns = ('name', 'description')
