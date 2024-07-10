"""notif_webhook_unifonic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include, re_path
from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('login/', views.Login.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('webhook/', include('webhook_receiver.urls')),
    path('webhook/', include('webhook_receiver.urls')),
#    re_path(r'^_status', include('health_check.urls')),
#    path('_status/', views.HealthCheckAPIVIEW.as_view(), name='status_view'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
