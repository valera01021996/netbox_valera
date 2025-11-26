from netbox.api.serializers import NetBoxModelSerializer
from ..models import DeviceScan

class DeviceScanSerializer(NetBoxModelSerializer):
    class Meta:
       model = DeviceScan
       fields = [
           'id', 'url', 'display', 'device', 'status',
           'last_started', 'last_finished', 'attemts', 'error',
           'custom_fields', 'created', 'last_updated', 'tags',
       ]