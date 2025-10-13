from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Farmer, Device, SensorData, AlertLog


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class FarmerSerializer(serializers.ModelSerializer):
    """Serializer for Farmer model"""
    user = UserSerializer(read_only=True)
    devices = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Farmer
        fields = ['id', 'user', 'phone_number', 'farm_name', 'farm_location', 
                 'ant_threshold_limit', 'created_at', 'updated_at', 'devices']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model"""
    farmer_name = serializers.CharField(source='farmer.user.username', read_only=True)
    sensor_data_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = ['id', 'device_id', 'device_name', 'location', 'is_active', 
                 'api_key', 'farmer', 'farmer_name', 'sensor_data_count', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'api_key', 'created_at', 'updated_at']
    
    def get_sensor_data_count(self, obj):
        """Get count of sensor data records for this device"""
        return obj.sensor_data.count()


class SensorDataSerializer(serializers.ModelSerializer):
    """Serializer for SensorData model"""
    device_name = serializers.CharField(source='device.device_name', read_only=True)
    farmer_name = serializers.CharField(source='device.farmer.user.username', read_only=True)
    
    class Meta:
        model = SensorData
        fields = ['id', 'device', 'device_name', 'farmer_name', 'timestamp', 
                 'temperature', 'humidity', 'moisture', 'ant_count', 'mealy_bugs_count', 
                 'is_rainfall', 'is_irrigation', 'ml_confidence', 'created_at']
        read_only_fields = ['id', 'created_at']


class DeviceDataSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for device data submission API (used by Raspberry Pi)"""
    
    class Meta:
        model = SensorData
        fields = ['timestamp', 'temperature', 'humidity', 'ant_count', 
                 'mealy_bugs_count', 'is_rainfall', 'is_irrigation']
    
    def create(self, validated_data):
        """Create sensor data record"""
        device = self.context['device']
        return SensorData.objects.create(device=device, **validated_data)


class AlertLogSerializer(serializers.ModelSerializer):
    """Serializer for AlertLog model"""
    device_name = serializers.CharField(source='sensor_data.device.device_name', read_only=True)
    
    class Meta:
        model = AlertLog
        fields = ['id', 'sensor_data', 'device_name', 'alert_type', 'message', 
                 'sent_at', 'sent_to']
        read_only_fields = ['id', 'sent_at']


class FarmerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for farmer registration"""
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Farmer
        fields = ['username', 'email', 'password', 'password_confirm', 'phone_number', 
                 'farm_name', 'farm_location', 'ant_threshold_limit']
    
    def validate(self, data):
        """Validate password confirmation and username uniqueness"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": ["A user with this username already exists."]})
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": ["A user with this email already exists."]})
        
        return data
    
    def create(self, validated_data):
        """Create user and farmer"""
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm')
        
        # Extract user data
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create farmer
        farmer = Farmer.objects.create(user=user, **validated_data)
        return farmer
