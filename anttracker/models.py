from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


class Farmer(models.Model):
    """Extended user model for farmers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    farm_name = models.CharField(max_length=200, blank=True, null=True)
    farm_location = models.CharField(max_length=300, blank=True, null=True)
    ant_threshold_limit = models.IntegerField(default=50, help_text="Ant count threshold for alerts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.farm_name}"

    class Meta:
        verbose_name = "Farmer"
        verbose_name_plural = "Farmers"


class Device(models.Model):
    """Model for Raspberry Pi devices"""
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=100, unique=True, help_text="Unique device identifier")
    device_name = models.CharField(max_length=200, help_text="Human readable device name")
    location = models.CharField(max_length=300, blank=True, null=True, help_text="Device location description")
    is_active = models.BooleanField(default=True, help_text="Whether device is currently active")
    api_key = models.CharField(max_length=100, unique=True, help_text="API key for device authentication")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"


class SensorData(models.Model):
    """Model for storing sensor data from devices"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sensor_data')
    timestamp = models.DateTimeField(default=timezone.now, help_text="When the data was recorded")
    temperature = models.FloatField(help_text="Temperature in Celsius")
    humidity = models.FloatField(help_text="Humidity percentage")
    moisture = models.FloatField(null=True, blank=True, help_text="Soil moisture percentage")
    ant_count = models.IntegerField(default=0, help_text="Number of ants detected by device-side ML")
    mealy_bugs_count = models.IntegerField(default=0, help_text="Number of mealy bugs detected by device-side ML")
    is_rainfall = models.BooleanField(default=False, help_text="Whether rainfall was detected")
    is_irrigation = models.BooleanField(default=False, help_text="Whether irrigation was active")
    ml_confidence = models.FloatField(null=True, blank=True, help_text="ML model confidence score from device")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.device_name} - {self.timestamp}"

    class Meta:
        verbose_name = "Sensor Data"
        verbose_name_plural = "Sensor Data"
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        """Override save to send email alerts when ant count exceeds threshold"""
        super().save(*args, **kwargs)
        
        # Check if ant count exceeds threshold
        if self.ant_count > self.device.farmer.ant_threshold_limit:
            self.send_ant_alert()

    def send_ant_alert(self):
        """Send email alert when ant count exceeds threshold"""
        try:
            subject = f"🚨 Ant Alert: High Ant Count Detected - {self.device.device_name}"
            message = f"""
Dear {self.device.farmer.user.first_name or self.device.farmer.user.username},

Your ant monitoring device "{self.device.device_name}" has detected an unusually high number of ants.

Alert Details:
- Device: {self.device.device_name}
- Location: {self.device.location or 'Not specified'}
- Ant Count: {self.ant_count}
- Threshold: {self.device.farmer.ant_threshold_limit}
- Temperature: {self.temperature}°C
- Humidity: {self.humidity}%
- Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Please check your farm and take necessary action if required.

Best regards,
MonitorMyBug System
            """
            
            recipient_email = self.device.farmer.user.email
            if recipient_email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL or 'noreply@monitormybug.com',
                    [recipient_email],
                    fail_silently=False,
                )
        except Exception as e:
            # Log the error but don't fail the save operation
            print(f"Failed to send ant alert email: {e}")


class AlertLog(models.Model):
    """Model to track sent alerts"""
    sensor_data = models.ForeignKey(SensorData, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=50, default='ant_threshold')
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_to = models.EmailField()

    def __str__(self):
        return f"Alert for {self.sensor_data.device.device_name} - {self.sent_at}"

    class Meta:
        verbose_name = "Alert Log"
        verbose_name_plural = "Alert Logs"
        ordering = ['-sent_at']
