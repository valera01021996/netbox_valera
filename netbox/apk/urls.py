from django.urls import path
from . import views

urlpatterns = [
    # APK Names
    path("names/", views.APKNameListView.as_view(), name="apkname_list"),
    path("names/add/", views.APKNameCreateView.as_view(), name="apkname_add"),
    path("names/<int:pk>/", views.APKNameDetailView.as_view(), name="apkname"),
    path("names/<int:pk>/edit/", views.APKNameEditView.as_view(), name="apkname_edit"),
    path("names/<int:pk>/delete/", views.APKNameDeleteView.as_view(), name="apkname_delete"),
    path("names/bulk-edit/", views.APKNameBulkEditView.as_view(), name="apkname_bulk_edit"),
    path("names/bulk-delete/", views.APKNameBulkDeleteView.as_view(), name="apkname_bulk_delete"),
        # APK Entries (главный список)
    path("", views.APKEntryListView.as_view(), name="apkentry_list"),
    path("add/", views.APKEntryCreateView.as_view(), name="apkentry_add"),
    path("<int:pk>/", views.APKEntryDetailView.as_view(), name="apkentry"),
    path("<int:pk>/edit/", views.APKEntryEditView.as_view(), name="apkentry_edit"),
    path("<int:pk>/delete/", views.APKEntryDeleteView.as_view(), name="apkentry_delete"),
    path("bulk-edit/", views.APKEntryBulkEditView.as_view(), name="apkentry_bulk_edit"),
    path("bulk-delete/", views.APKEntryBulkDeleteView.as_view(), name="apkentry_bulk_delete"),
    path('names/<int:pk>/devices/', views.APKNameDevicesView.as_view(), name='apkname_devices'),
    path('entries/<int:pk>/devices/', views.APKNameDevicesView.as_view(), name='apkentry_devices'),
]