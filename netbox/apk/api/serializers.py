from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import APKService

class APKServiceSerializer(NetBoxModelSerializer):
    class Meta:
        model = APKService
        fields = '__all__'