from netbox.api.viewsets import NetBoxModelViewSet
from ..models import DeviceScan
from .serializers import DeviceScanSerializer

class DeviceScanViewSet(NetBoxModelViewSet):
    queryset = DeviceScan.objects.order_by('pk')
    serializer_class = DeviceScanSerializer