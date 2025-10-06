from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def login_page(request):
    """Serve the login page"""
    if request.user.is_authenticated:
        # Check if user has a farmer profile
        try:
            farmer = request.user.farmer
            return redirect('dashboard-page')
        except:
            # User is authenticated but doesn't have farmer profile, redirect to register
            return redirect('register-page')
    return render(request, 'anttracker/login.html')


def register_page(request):
    """Serve the registration page"""
    if request.user.is_authenticated:
        # Check if user already has a farmer profile
        try:
            farmer = request.user.farmer
            return redirect('dashboard-page')
        except:
            # User is authenticated but doesn't have farmer profile, show registration
            pass
    return render(request, 'anttracker/register.html')


def dashboard_page(request):
    """Serve the dashboard page"""
    if not request.user.is_authenticated:
        return redirect('login-page')
    
    try:
        # Check if user has a farmer profile
        farmer = request.user.farmer
        return render(request, 'anttracker/dashboard.html', {'farmer': farmer})
    except:
        # If user doesn't have farmer profile, redirect to register
        messages.error(request, 'Please complete your farmer profile registration.')
        return redirect('register-page')


@csrf_exempt
def logout_view(request):
    """Logout view - handles both GET and POST requests"""
    django_logout(request)
    
    # If it's a POST request (AJAX), return JSON response
    if request.method == 'POST':
        return JsonResponse({'success': True, 'message': 'Logged out successfully'})
    
    # If it's a GET request, redirect to login page
    return redirect('login-page')
