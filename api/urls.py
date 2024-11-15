from django.urls import path
from . import views

urlpatterns = [
    path('companies/', views.get_companies, name='get_companies'),
    path('chart-of-accounts/<str:company_name>/', views.get_chart_of_accounts, name='get_chart_of_accounts'),
    path('list-of-vouchers/<str:company_name>/', views.get_list_of_vouchers, name='get_list_of_vouchers'),
    path('create-ledger/', views.create_ledger, name='create_ledger'),
]
