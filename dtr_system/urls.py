from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static
import os
from accounts import views as accounts_views

urlpatterns = [
    path('', accounts_views.login_view, name='login'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/clear/', core_views.clear_data, name='clear_data'),
    path('ai/', accounts_views.ai_assistant, name='ai_assistant'),
    path('ai_query_stream/', accounts_views.ai_query_stream, name='ai_query_stream'),
    path('upload_file/', accounts_views.upload_file, name='upload_file'),
    path('user-info-api/<int:user_id>/', accounts_views.user_info_api, name='user_info_api'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static('/static/', document_root=settings.STATIC_ROOT)
    urlpatterns += static('/static/backups/', document_root=os.path.join(settings.BASE_DIR, 'backups'))