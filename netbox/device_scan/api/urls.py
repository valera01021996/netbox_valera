from netbox.api.routers import NetBoxRouter
from . import viewsets

app_name = 'device_scan-api'

router = NetBoxRouter()
router.register('device-scans', viewsets.DeviceScanViewSet)

urlpatterns = router.urls
