from netbox.api.routers import NetBoxRouter
from .viewsets import APKServiceViewSet

router = NetBoxRouter()
router.register('apk-services', APKServiceViewSet)  # /api/plugins/apk/apk-services/

app_name = 'apk'
urlpatterns = router.urls