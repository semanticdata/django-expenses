from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.home, name='home'),
    path('export/', views.export_data, name='export_data'),
    path('import/', views.import_data, name='import_data'),
    path('chart/expense-data/', views.expense_chart_data, name='expense_chart_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
] 