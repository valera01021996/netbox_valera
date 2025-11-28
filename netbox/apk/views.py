from django.urls import reverse
from netbox.views import generic
from .models import APK
from .tables import APKTable, APKDRSTable, APKRubejTable
from .forms import APKForm, APKDRSForm, APKRubejForm
from netbox.object_actions import AddObject, BulkDelete


class APKHSIListView(generic.ObjectListView):
    # Показываем только объекты, где type не равен 'DRS' и не равен 'Rubej'
    queryset = APK.objects.exclude(type__iexact='DRS').exclude(type__iexact='Rubej').order_by('name', 'pk')
    table = APKTable
    actions = (AddObject, BulkDelete)


class APKHSIEditView(generic.ObjectEditView):
    queryset = APK.objects.exclude(type__iexact='DRS').exclude(type__iexact='Rubej').order_by('name', 'pk')
    form = APKForm


class APKHSIView(generic.ObjectView):
    queryset = APK.objects.exclude(type__iexact='DRS').exclude(type__iexact='Rubej').order_by('name', 'pk')


class APKHSIDeleteView(generic.ObjectDeleteView):
    queryset = APK.objects.exclude(type__iexact='DRS').exclude(type__iexact='Rubej').order_by('name', 'pk')


class APKHSIChangeLogView(generic.ObjectChangeLogView):
    queryset = APK.objects.exclude(type__iexact='DRS').exclude(type__iexact='Rubej').order_by('name', 'pk')


class APKHSIBulkDeleteView(generic.BulkDeleteView):
    queryset = APK.objects.exclude(type__iexact='DRS').exclude(type__iexact='Rubej').order_by('name', 'pk')
    table = APKTable


class AddAPKDRSObject(AddObject):
    """Кастомный AddObject для APK DRS, который всегда ведет на drs/add"""
    @classmethod
    def get_url(cls, obj):
        return reverse('plugins:apk:apk_drs_add')


class BulkDeleteAPKDRS(BulkDelete):
    """Кастомный BulkDelete для APK DRS, который всегда ведет на drs/delete"""
    @classmethod
    def get_url(cls, obj):
        return reverse('plugins:apk:apk_drs_bulk_delete')


class APKDRSListView(generic.ObjectListView):
    # Показываем только объекты, где type равен 'DRS'
    queryset = APK.objects.filter(type__iexact='DRS').order_by('name', 'pk')
    table = APKDRSTable
    actions = (AddAPKDRSObject, BulkDeleteAPKDRS)


class APKDRSEditView(generic.ObjectEditView):
    queryset = APK.objects.filter(type__iexact='DRS').order_by('name', 'pk')
    form = APKDRSForm


class APKDRSView(generic.ObjectView):
    queryset = APK.objects.filter(type__iexact='DRS').order_by('name', 'pk')
    template_name = 'apk/apkdrs.html'


class APKDRSDeleteView(generic.ObjectDeleteView):
    queryset = APK.objects.filter(type__iexact='DRS').order_by('name', 'pk')


class APKDRSChangeLogView(generic.ObjectChangeLogView):
    queryset = APK.objects.filter(type__iexact='DRS').order_by('name', 'pk')


class APKDRSBulkDeleteView(generic.BulkDeleteView):
    queryset = APK.objects.filter(type__iexact='DRS').order_by('name', 'pk')
    table = APKDRSTable


class AddAPKRubejObject(AddObject):
    """Кастомный AddObject для APK Rubej, который всегда ведет на rubej/add"""
    @classmethod
    def get_url(cls, obj):
        return reverse('plugins:apk:apk_rubej_add')


class BulkDeleteAPKRubej(BulkDelete):
    """Кастомный BulkDelete для APK Rubej, который всегда ведет на rubej/delete"""
    @classmethod
    def get_url(cls, obj):
        return reverse('plugins:apk:apk_rubej_bulk_delete')


class APKRubejListView(generic.ObjectListView):
    queryset = APK.objects.filter(type__iexact='Rubej').order_by('name', 'pk')
    table = APKRubejTable
    actions = (AddAPKRubejObject, BulkDeleteAPKRubej)


class APKRubejEditView(generic.ObjectEditView):
    queryset = APK.objects.filter(type__iexact='Rubej').order_by('name', 'pk')
    form = APKRubejForm


class APKRubejView(generic.ObjectView):
    queryset = APK.objects.filter(type__iexact='Rubej').order_by('name', 'pk')
    template_name = 'apk/apkrubej.html'


class APKRubejDeleteView(generic.ObjectDeleteView):
    queryset = APK.objects.filter(type__iexact='Rubej').order_by('name', 'pk')


class APKRubejChangeLogView(generic.ObjectChangeLogView):
    queryset = APK.objects.filter(type__iexact='Rubej').order_by('name', 'pk')


class APKRubejBulkDeleteView(generic.BulkDeleteView):
    queryset = APK.objects.filter(type__iexact='Rubej').order_by('name', 'pk')
    table = APKRubejTable