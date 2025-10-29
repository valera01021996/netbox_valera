from netbox.views import generic
from .models import APKService
from .tables import APKServiceTable
from .forms import APKServiceForm, APKServiceBulkEditForm


class APKServiceListView(generic.ObjectListView):
    queryset = APKService.objects.all()
    table = APKServiceTable

    def get_queryset(self, request):
        # убираем фильтрацию по разрешениям
        return APKService.objects.all()

class APKServiceDetailView(generic.ObjectView):
        queryset = APKService.objects.all()
        template_name = 'generic/object.html'

class APKServiceEditView(generic.ObjectEditView):
    queryset = APKService.objects.all()
    form = APKServiceForm

class APKServiceDeleteView(generic.ObjectDeleteView):
    queryset = APKService.objects.all()

class APKServiceCreateView(generic.ObjectEditView):
    queryset = APKService.objects.all()
    form = APKServiceForm

class APKServiceBulkDeleteView(generic.BulkDeleteView):
    queryset = APKService.objects.all()
    table = APKServiceTable

class APKServiceBulkEditView(generic.BulkEditView):
    queryset = APKService.objects.all()
    table = APKServiceTable
    form = APKServiceBulkEditForm