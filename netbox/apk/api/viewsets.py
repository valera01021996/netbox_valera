from netbox.api.viewsets import NetBoxModelViewSet
from ..models import APKService
from .serializers import APKServiceSerializer

class APKServiceViewSet(NetBoxModelViewSet):
    queryset = APKService.objects.all()
    serializer_class = APKServiceSerializer