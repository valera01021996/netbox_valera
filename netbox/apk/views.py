from netbox.views import generic
from .models import APK
from .tables import APKTable
from .forms import APKForm
from netbox.object_actions import AddObject, BulkDelete


class APKListView(generic.ObjectListView):
    queryset = APK.objects.order_by('name', 'pk')
    table = APKTable
    actions = (AddObject, BulkDelete)


class APKEditView(generic.ObjectEditView):
    queryset = APK.objects.order_by('name', 'pk')
    form = APKForm


class APKView(generic.ObjectView):
    queryset = APK.objects.order_by('name', 'pk')


class APKDeleteView(generic.ObjectDeleteView):
    queryset = APK.objects.order_by('name', 'pk')


class APKChangeLogView(generic.ObjectChangeLogView):
    queryset = APK.objects.order_by('name', 'pk')


class APKBulkDeleteView(generic.BulkDeleteView):
    queryset = APK.objects.order_by('name', 'pk')
    table = APKTable