from netbox.api.viewsets import NetBoxModelViewSet

from ..models import APK
from .serializers import APKSerializer, APKDRSSerializer


class APKViewSet(NetBoxModelViewSet):
    queryset = APK.objects.order_by('name', 'pk')
    serializer_class = APKSerializer


class APKDRSViewSet(NetBoxModelViewSet):
    # Показываем только объекты, где type равен 'DRS'
    queryset = APK.objects.filter(type__iexact='DRS').order_by('name', 'pk')
    serializer_class = APKDRSSerializer
