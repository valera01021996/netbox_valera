import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import APKName, APKEntry

class APKNameTable(NetBoxTable):
    name = tables.Column()
    actions = columns.ActionsColumn(actions=("edit", "delete"))

    class Meta(NetBoxTable.Meta):
        model = APKName
        fields = ("name", "description", "created")
        default_columns = ("name", "description")


class APKEntryTable(NetBoxTable):
    exempt_columns = ('pk', 'expand', 'actions')
    
    expand = columns.TemplateColumn(
        template_code="""
        <button type="button" class="btn btn-xs btn-outline-secondary toggle-details" data-apk="{{ record.pk }}">
            <i class="mdi mdi-chevron-down"></i>
        </button>
        """,
        verbose_name="",
        orderable=False
    )
    apk_name = tables.Column(verbose_name="APK Name")
    devices = tables.TemplateColumn(
        verbose_name="Devices",
        template_code="""
          <a href="{% url 'plugins:apk:apkentry_devices' record.pk %}">{{ record.devices_count }}</a>
        """,
        orderable=False,
    )
    apk_type = tables.Column(verbose_name="Тип АПК")
    operator = tables.Column(verbose_name="Оператор", linkify=True)
    contract = tables.Column(verbose_name="Договор")
    ports_count = tables.Column(verbose_name="Кол-во портов")
    capacity_mbps = tables.Column(verbose_name="Ёмкость лицензии")
    ports_type = tables.Column(verbose_name="Тип портов")
    specs = tables.Column(verbose_name="ТТХ")
    actions = columns.ActionsColumn(actions=("edit", "delete"))

    class Meta(NetBoxTable.Meta):
        model = APKEntry
        fields = (
            "pk",
            "expand",
            "apk_name",
            "apk_type",
            "operator",
            "contract",
            "ports_count",
            "capacity_mbps",
            "ports_type",
            "specs",
            "devices",
            "actions",
        )
        default_columns = (
            "pk",
            "expand",
            "apk_name",
            "apk_type",
            "operator",
            "ports_count",
            "capacity_mbps",
            "ports_type",
            "devices",
            "actions",
        )
        row_attrs = {
            "data-ports-count": lambda record: str(record.ports_count) if record.ports_count else "",
            "data-ports-type": lambda record: str(record.ports_type) if record.ports_type else "",
            "data-capacity": lambda record: str(record.capacity_mbps) if record.capacity_mbps else "",
         }
