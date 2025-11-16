from netbox.api.viewsets import NetBoxModelViewSet

from ..models import APK
from .serializers import APKSerializer


class APKViewSet(NetBoxModelViewSet):
    queryset = APK.objects.order_by('name', 'pk')
    serializer_class = APKSerializer