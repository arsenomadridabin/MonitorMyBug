from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.utils.crypto import get_random_string
from django.db.models import Q, Avg, Max
from django.utils import timezone
from datetime import timedelta
from .models import Farmer, Device, SensorData, AlertLog
from .serializers import (
    FarmerSerializer, DeviceSerializer, SensorDataSerializer, 
    DeviceDataSubmissionSerializer, AlertLogSerializer, FarmerRegistrationSerializer
)


class FarmerRegistrationView(generics.CreateAPIView):
    """API view for farmer registration"""
    queryset = Farmer.objects.all()
    serializer_class = FarmerRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        farmer = serializer.save()
        
        # Create auth token for the user
        token, created = Token.objects.get_or_create(user=farmer.user)
        
        return Response({
            'message': 'Farmer registered successfully',
            'farmer_id': farmer.id,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def farmer_login(request):
    """API view for farmer login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        farmer = user.farmer
    except Farmer.DoesNotExist:
        return Response({
            'error': 'User is not a farmer'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Create or get auth token
    token, created = Token.objects.get_or_create(user=user)
    
    # Log the user in using Django's session authentication
    login(request, user)
    
    return Response({
        'message': 'Login successful',
        'farmer_id': farmer.id,
        'token': token.key,
        'farmer': FarmerSerializer(farmer).data
    })


class DeviceListView(generics.ListCreateAPIView):
    """API view for listing and creating devices"""
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return devices for the authenticated farmer"""
        try:
            farmer = self.request.user.farmer
            return Device.objects.filter(farmer=farmer)
        except Farmer.DoesNotExist:
            return Device.objects.none()
    
    def perform_create(self, serializer):
        """Create device for the authenticated farmer"""
        farmer = self.request.user.farmer
        # Generate unique API key
        api_key = get_random_string(32)
        serializer.save(farmer=farmer, api_key=api_key)


class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for device detail operations"""
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return devices for the authenticated farmer"""
        try:
            farmer = self.request.user.farmer
            return Device.objects.filter(farmer=farmer)
        except Farmer.DoesNotExist:
            return Device.objects.none()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def device_data_submission(request, device_id):
    """API view for device data submission (used by Raspberry Pi)"""
    api_key = request.headers.get('Authorization')
    
    if not api_key:
        return Response({
            'error': 'API key is required'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Remove 'Bearer ' prefix if present
    if api_key.startswith('Bearer '):
        api_key = api_key[7:]
    
    try:
        device = Device.objects.get(device_id=device_id, api_key=api_key, is_active=True)
    except Device.DoesNotExist:
        return Response({
            'error': 'Invalid device ID or API key'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = DeviceDataSubmissionSerializer(data=request.data, context={'device': device})
    if serializer.is_valid():
        sensor_data = serializer.save()
        return Response({
            'message': 'Data submitted successfully',
            'data_id': sensor_data.id,
            'timestamp': sensor_data.timestamp
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FarmerDashboardView(generics.ListAPIView):
    """API view for farmer dashboard data"""
    serializer_class = SensorDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return recent sensor data for farmer's devices"""
        try:
            farmer = self.request.user.farmer
            queryset = SensorData.objects.filter(device__farmer=farmer)
            
            # Check for date filtering
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            
            if start_date:
                queryset = queryset.filter(timestamp__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(timestamp__date__lte=end_date)
            
            # If no date filter, get data from last 24 hours by default
            if not start_date and not end_date:
                yesterday = timezone.now() - timedelta(hours=24)
                queryset = queryset.filter(timestamp__gte=yesterday)
            
            return queryset.order_by('-timestamp')
        except Farmer.DoesNotExist:
            return SensorData.objects.none()
    
    def list(self, request, *args, **kwargs):
        """Return dashboard data with summary statistics"""
        queryset = self.get_queryset()
        
        # Limit sensor data to last 100 records for performance
        limited_queryset = queryset[:100]
        serializer = self.get_serializer(limited_queryset, many=True)
        
        # Calculate summary statistics
        farmer = request.user.farmer
        devices = Device.objects.filter(farmer=farmer)
        total_devices = devices.count()
        
        # Active devices = devices that have sent data in last 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        active_devices = devices.filter(
            sensor_data__timestamp__gte=yesterday
        ).distinct().count()
        
        # Calculate average temperature from current queryset (respects date filter)
        if queryset.exists():
            avg_temperature = queryset.aggregate(
                avg_temp=Avg('temperature')
            )['avg_temp'] or 0
            avg_humidity = queryset.aggregate(
                avg_hum=Avg('humidity')
            )['avg_hum'] or 0
            max_ant_count = queryset.aggregate(
                max_ants=Max('ant_count')
            )['max_ants'] or 0
        else:
            avg_temperature = 0
            avg_humidity = 0
            max_ant_count = 0
        
        # Recent alerts = sensor readings with ant count above threshold in current period
        recent_alerts = queryset.filter(
            ant_count__gt=farmer.ant_threshold_limit
        ).count()
        
        # Get latest data for each device
        latest_data = {}
        for device in devices:
            latest_sensor_data = device.sensor_data.first()
            if latest_sensor_data:
                latest_data[device.device_name] = {
                    'timestamp': latest_sensor_data.timestamp,
                    'ant_count': latest_sensor_data.ant_count,
                    'temperature': latest_sensor_data.temperature,
                    'humidity': latest_sensor_data.humidity
                }
        
        return Response({
            'sensor_data': serializer.data,
            'summary': {
                'total_devices': total_devices,
                'active_devices': active_devices,
                'recent_alerts': recent_alerts,
                'avg_temperature': round(avg_temperature, 1),
                'avg_humidity': round(avg_humidity, 1),
                'max_ant_count': max_ant_count,
                'latest_data': latest_data
            }
        })


class SensorDataListView(generics.ListAPIView):
    """API view for listing sensor data"""
    serializer_class = SensorDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return sensor data for farmer's devices"""
        try:
            farmer = self.request.user.farmer
            queryset = SensorData.objects.filter(device__farmer=farmer)
            
            # Filter by device if specified
            device_id = self.request.query_params.get('device_id')
            if device_id:
                queryset = queryset.filter(device__device_id=device_id)
            
            # Filter by date range if specified
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            if start_date:
                queryset = queryset.filter(timestamp__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(timestamp__date__lte=end_date)
            
            return queryset.order_by('-timestamp')
        except Farmer.DoesNotExist:
            return SensorData.objects.none()


class AlertLogListView(generics.ListAPIView):
    """API view for listing alert logs"""
    serializer_class = AlertLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return alert logs for farmer's devices"""
        try:
            farmer = self.request.user.farmer
            return AlertLog.objects.filter(
                sensor_data__device__farmer=farmer
            ).order_by('-sent_at')
        except Farmer.DoesNotExist:
            return AlertLog.objects.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def farmer_profile(request):
    """API view for farmer profile"""
    try:
        farmer = request.user.farmer
        serializer = FarmerSerializer(farmer)
        return Response(serializer.data)
    except Farmer.DoesNotExist:
        return Response({
            'error': 'Farmer profile not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_farmer_profile(request):
    """API view for updating farmer profile"""
    try:
        farmer = request.user.farmer
        serializer = FarmerSerializer(farmer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'farmer': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Farmer.DoesNotExist:
        return Response({
            'error': 'Farmer profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
