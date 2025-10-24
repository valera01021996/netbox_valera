from django.urls import path
from . import views

app_name = 'nb_automation'

urlpatterns = [
    path('excel-upload/', views.ExcelUploadView.as_view(), name='excel_upload'),
]
