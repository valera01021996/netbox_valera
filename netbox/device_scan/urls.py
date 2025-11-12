from django.urls import path
from django.http import HttpResponse
from . import views


def dummy_edit_view(request, pk):
    return HttpResponse("Редактирование недоступно.", content_type="text/plain")

def dummy_delete_view(request, pk):
    return HttpResponse("Редактирование недоступно.", content_type="text/plain")

def dummy_changelog_view(request, pk):
    return HttpResponse("История изменений недоступна.", content_type="text/plain")

urlpatterns = [
    path("scans/", views.DeviceScanListView.as_view(), name="devicescan_list"),
    path("scans/<int:pk>/", views.DeviceScanView.as_view(), name="devicescan_view"),
    path("scans/<int:pk>/edit/", dummy_edit_view, name="devicescan_edit"),
    path("scans/<int:pk>/delete/", dummy_delete_view, name="devicescan_delete"),
    path("scans/<int:pk>/changelog/", dummy_changelog_view, name="devicescan_changelog"),
]