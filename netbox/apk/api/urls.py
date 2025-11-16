from netbox.api.routers import NetBoxRouter

from . import viewsets

app_name = 'apk-api'

router = NetBoxRouter()
router.register('apk', viewsets.APKViewSet)

urlpatterns = router.urls

