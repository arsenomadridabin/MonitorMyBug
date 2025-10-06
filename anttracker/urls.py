from django.urls import path
from . import views
from . import template_views

urlpatterns = [
    # Web pages
    path('login.html', template_views.login_page, name='login-page'),
    path('register.html', template_views.register_page, name='register-page'),
    path('dashboard.html', template_views.dashboard_page, name='dashboard-page'),
    path('logout/', template_views.logout_view, name='logout'),
    
    # API Authentication endpoints
    path('register/', views.FarmerRegistrationView.as_view(), name='farmer-register'),
    path('login/', views.farmer_login, name='farmer-login'),
    
    # Farmer profile endpoints
    path('profile/', views.farmer_profile, name='farmer-profile'),
    path('profile/update/', views.update_farmer_profile, name='update-farmer-profile'),
    
    # Device management endpoints
    path('devices/', views.DeviceListView.as_view(), name='device-list'),
    path('devices/<int:pk>/', views.DeviceDetailView.as_view(), name='device-detail'),
    
    # Device data submission endpoint (for Raspberry Pi)
    path('device-data/<str:device_id>/', views.device_data_submission, name='device-data-submission'),
    
    # Dashboard and data endpoints
    path('dashboard/', views.FarmerDashboardView.as_view(), name='farmer-dashboard'),
    path('sensor-data/', views.SensorDataListView.as_view(), name='sensor-data-list'),
    path('alerts/', views.AlertLogListView.as_view(), name='alert-log-list'),
]
