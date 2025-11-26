from django.urls import path

from . import views

app_name = 'apk'

urlpatterns = [
    path("hsi/", views.APKHSIListView.as_view(), name="apk_hsi_list"),
    path('hsi/add/', views.APKHSIEditView.as_view(), name='apk_hsi_add'),
    path('hsi/<int:pk>/', views.APKHSIView.as_view(), name='apk_hsi'),
    path('hsi/<int:pk>/edit/', views.APKHSIEditView.as_view(), name='apk_hsi_edit'),
    path('hsi/<int:pk>/delete/', views.APKHSIDeleteView.as_view(), name='apk_hsi_delete'),
    path('hsi/<int:pk>/changelog/', views.APKHSIChangeLogView.as_view(), name='apk_hsi_changelog'),
    path('hsi/delete/', views.APKHSIBulkDeleteView.as_view(), name='apk_hsi_bulk_delete'),
]

urlpatterns += [
    path("drs/", views.APKDRSListView.as_view(), name="apk_drs_list"),
    path('drs/add/', views.APKDRSEditView.as_view(), name='apk_drs_add'),
    path('drs/<int:pk>/', views.APKDRSView.as_view(), name='apk_drs'),
    path('drs/<int:pk>/edit/', views.APKDRSEditView.as_view(), name='apk_drs_edit'),
    path('drs/<int:pk>/delete/', views.APKDRSDeleteView.as_view(), name='apk_drs_delete'),
    path('drs/<int:pk>/changelog/', views.APKDRSChangeLogView.as_view(), name='apk_drs_changelog'),
    path('drs/delete/', views.APKDRSBulkDeleteView.as_view(), name='apk_drs_bulk_delete'),
]

urlpatterns += [
    path("rubej/", views.APKRubejListView.as_view(), name="apk_rubej_list"),
    # path('rubej/add/', views.APKRubejEditView.as_view(), name='apk_rubej_add'),
    # path('rubej/<int:pk>/', views.APKRubejView.as_view(), name='apk_rubej'),
    # path('rubej/<int:pk>/edit/', views.APKRubejEditView.as_view(), name='apk_rubej_edit'),
    # path('rubej/<int:pk>/delete/', views.APKRubejDeleteView.as_view(), name='apk_rubej_delete'),
    # path('rubej/<int:pk>/changelog/', views.APKRubejChangeLogView.as_view(), name='apk_rubej_changelog'),
    # path('rubej/delete/', views.APKRubejBulkDeleteView.as_view(), name='apk_rubej_bulk_delete'),
]