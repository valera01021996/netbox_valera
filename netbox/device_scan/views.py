from django.views.generic import ListView
from netbox.views.generic import ObjectListView, ObjectView
from .models import DeviceScan
from .tables import DeviceScanTable

    
class DeviceScanListView(ObjectListView):
    queryset = DeviceScan.objects.select_related("device")
    table = DeviceScanTable
    


class DeviceScanView(ObjectView):
    queryset = DeviceScan.objects.all()