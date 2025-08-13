"""
URL configuration for dtr_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import admin_dashboard, client_dashboard
from django.conf import settings
from django.conf.urls.static import static
from core import views
import os

urlpatterns = [
    path('', include('accounts.urls')),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/client/', client_dashboard, name='client_dashboard'),
    path('dashboard/clear/', views.clear_data, name='clear_data'),
    path('accounts/', include('accounts.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# This file defines the URL patterns for the dtr_system project, including admin and dashboard views.
# The admin site is included for development purposes, and the dashboard paths are defined for both admin

if settings.DEBUG:
    urlpatterns += static('/static/', document_root=settings.STATIC_ROOT)
    urlpatterns += static('/static/backups/', document_root=os.path.join(settings.BASE_DIR, 'backups'))