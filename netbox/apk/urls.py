from django.urls import path

from . import views

app_name = 'apk'

urlpatterns = [
    path("", views.APKListView.as_view(), name="apk_list"),
    path('add/', views.APKEditView.as_view(), name='apk_add'),
    path('<int:pk>/', views.APKView.as_view(), name='apk'),
    path('<int:pk>/edit/', views.APKEditView.as_view(), name='apk_edit'),
    path('<int:pk>/delete/', views.APKDeleteView.as_view(), name='apk_delete'),
    path('<int:pk>/changelog/', views.APKChangeLogView.as_view(), name='apk_changelog'),
    path('delete/', views.APKBulkDeleteView.as_view(), name='apk_bulk_delete'),
]