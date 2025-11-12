from netbox.api.viewsets import NetBoxModelViewSet
from apk.models import APKName, APKEntry
from .serializers import APKNameSerializer, APKEntrySerializer

class APKNameViewSet(NetBoxModelViewSet):
    queryset = APKName.objects.all()
    serializer_class = APKNameSerializer

class APKEntryViewSet(NetBoxModelViewSet):
    queryset = APKEntry.objects.all()
    serializer_class = APKEntrySerializer