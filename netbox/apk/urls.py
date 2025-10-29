from django.urls import path
from . import views

urlpatterns = [
    path('', views.APKServiceListView.as_view(), name='apkservice_list'),
    path('add/', views.APKServiceCreateView.as_view(), name='apkservice_add'),
    path('<int:pk>/edit/', views.APKServiceEditView.as_view(), name='apkservice_edit'),
    path('<int:pk>/delete/', views.APKServiceDeleteView.as_view(), name='apkservice_delete'),
    path('<int:pk>/', views.APKServiceDetailView.as_view(), name='apkservice'),
    path('bulk-delete/', views.APKServiceBulkDeleteView.as_view(), name='apkservice_bulk_delete'),
    path('bulk-edit/', views.APKServiceBulkEditView.as_view(), name='apkservice_bulk_edit'),
]
