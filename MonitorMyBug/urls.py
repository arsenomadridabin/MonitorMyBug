"""
URL configuration for MonitorMyBug project.

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
from django.http import JsonResponse
from django.shortcuts import redirect

def api_root(request):
    """API root endpoint with available endpoints"""
    return JsonResponse({
        'message': 'MonitorMyBug API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': '/api/register/',
                'login': '/api/login/',
            },
            'profile': {
                'get_profile': '/api/profile/',
                'update_profile': '/api/profile/update/',
            },
            'devices': {
                'list_devices': '/api/devices/',
                'device_detail': '/api/devices/{id}/',
                'device_data_submission': '/api/device-data/{device_id}/',
            },
            'dashboard': {
                'dashboard': '/api/dashboard/',
                'sensor_data': '/api/sensor-data/',
                'alerts': '/api/alerts/',
            },
            'admin': '/admin/',
        }
    })

def home_redirect(request):
    """Redirect root URL to dashboard"""
    return redirect('/dashboard.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('anttracker.urls')),
    path('api-docs/', api_root, name='api-root'),  # Move API docs to /api-docs/
    path('', home_redirect, name='home'),  # Redirect root to dashboard
]

# Import template views directly for root-level access
from anttracker import template_views

# Add template views at root level
urlpatterns += [
    path('login.html', template_views.login_page, name='login-page'),
    path('register.html', template_views.register_page, name='register-page'),
    path('dashboard.html', template_views.dashboard_page, name='dashboard-page'),
    path('logout/', template_views.logout_view, name='logout'),
]
