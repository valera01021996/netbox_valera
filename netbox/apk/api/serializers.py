from netbox.api.serializers import NetBoxModelSerializer
from apk.models import APKName, APKEntry

class APKNameSerializer(NetBoxModelSerializer):
    class Meta:
        model = APKName
        fields = '__all__'

class APKEntrySerializer(NetBoxModelSerializer):
    class Meta:
        model = APKEntry
        fields = '__all__'