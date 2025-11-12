from netbox.views import generic
from .models import APKName, APKEntry
from dcim.models import Device
from dcim.tables import DeviceTable
from .tables import APKNameTable, APKEntryTable
from .forms import APKNameForm, APKNameBulkEditForm, APKEntryForm, APKEntryBulkEditForm

class APKNameListView(generic.ObjectListView):
    queryset = APKName.objects.all()
    table = APKNameTable

class APKNameDetailView(generic.ObjectView):
    queryset = APKName.objects.all()
    # template_name = "generic/object.html"  # можно свой шаблон apk/apkname.html
    template_name = "apk/apkname.html"

class APKNameCreateView(generic.ObjectEditView):
    queryset = APKName.objects.all()
    form = APKNameForm

class APKNameEditView(generic.ObjectEditView):
    queryset = APKName.objects.all()
    form = APKNameForm

class APKNameDeleteView(generic.ObjectDeleteView):
    queryset = APKName.objects.all()

class APKNameBulkEditView(generic.BulkEditView):
    queryset = APKName.objects.all()
    table = APKNameTable
    form = APKNameBulkEditForm

class APKNameBulkDeleteView(generic.BulkDeleteView):
    queryset = APKName.objects.all()
    table = APKNameTable





class APKEntryListView(generic.ObjectListView):
    queryset = APKEntry.objects.all()
    table = APKEntryTable
    template_name = "apk/apkentry_list.html"

class APKEntryDetailView(generic.ObjectView):
    queryset = APKEntry.objects.all()
    template_name = "generic/object.html"  # или свой шаблон apk/apkentry.html

class APKEntryCreateView(generic.ObjectEditView):
    queryset = APKEntry.objects.all()
    form = APKEntryForm

class APKEntryEditView(generic.ObjectEditView):
    queryset = APKEntry.objects.all()
    form = APKEntryForm

class APKEntryDeleteView(generic.ObjectDeleteView):
    queryset = APKEntry.objects.all()

class APKEntryBulkEditView(generic.BulkEditView):
    queryset = APKEntry.objects.all()
    table = APKEntryTable
    form = APKEntryBulkEditForm

class APKEntryBulkDeleteView(generic.BulkDeleteView):
    queryset = APKEntry.objects.all()
    table = APKEntryTable



class APKNameDevicesView(generic.ObjectChildrenView):
    queryset = APKEntry.objects.all()
    child_model = Device
    table = DeviceTable
    template_name = 'generic/object_children.html'
    base_template = 'generic/object.html'

    def get_children(self, request, parent):
        return parent.devices_qs()
