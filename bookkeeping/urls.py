from django.urls import path
from . import views

urlpatterns = [
    path('', views.ledger_dashboard, name='ledger_dashboard'),
    path('export-csv/', views.export_ledger_csv, name='export_ledger_csv'),
]