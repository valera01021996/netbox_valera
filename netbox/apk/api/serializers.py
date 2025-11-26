from netbox.api.serializers import NetBoxModelSerializer

from ..models import APK


class APKSerializer(NetBoxModelSerializer):
    class Meta:
        model = APK
        fields = [
            'id',
            'url',
            'display',
            'name',
            'type',
            'operator',
            'region',
            'contract',
            'ttx',
            'port_type',
            'ports_count',
            'capacity',
            'avg_traffic',
            'retention_period',
            'custom_fields',
            'created',
            'last_updated',
            'tags',
        ]


class APKDRSSerializer(NetBoxModelSerializer):
    class Meta:
        model = APK  # Работаем с той же моделью APK
        fields = [
            'id',
            'url',
            'display',
            'name',
            'type',
            'operator',
            'region',
            'contract',
            'avg_traffic',
            'retention_period',
            'custom_fields',
            'created',
            'last_updated',
            'tags',
        ]
