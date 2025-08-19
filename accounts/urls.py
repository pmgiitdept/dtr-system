from django.urls import path
from accounts.views import login_view, logout_view
from core.views import admin_dashboard, client_dashboard
from . import views

urlpatterns = [
    path('', login_view, name='login'),  # http://127.0.0.1:8000/accounts/
    path('logout/', logout_view, name='logout'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),  # http://127.0.0.1:8000/accounts/dashboard/admin/
    path('dashboard/client/', client_dashboard, name='client_dashboard'),
    path('accounts-list/', views.accounts_list, name='accounts_list'),
    path('edit-account/<int:user_id>/', views.edit_account, name='edit_account'),
    path('accounts/delete/<int:account_id>/', views.delete_account, name='delete_account'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('api/user-info/<int:user_id>/', views.user_info_api, name='user_info_api'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('admin-settings/', views.admin_settings, name='admin_settings'),
    path('download-backup/<str:filename>/', views.download_backup, name='download_backup'),
    path('client-side/', views.client_side_view, name='client_side_view'),
    path('accounts/file-delete/<int:file_id>/', views.delete_uploaded_file, name='delete_uploaded_file'),
    path('user-info-api/<int:user_id>/', views.user_info_api, name='user_info_api'),
    path('ai_query_stream/', views.ai_query_stream, name='ai_query_stream'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('generate_chart/', views.generate_chart, name='generate_chart'),
]
