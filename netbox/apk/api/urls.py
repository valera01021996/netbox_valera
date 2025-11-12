from netbox.api.routers import NetBoxRouter
from .viewsets import APKNameViewSet, APKEntryViewSet

router = NetBoxRouter()
router.register('apk-names', APKNameViewSet)
router.register('apk-entries', APKEntryViewSet)

app_name = 'apk'
urlpatterns = router.urls