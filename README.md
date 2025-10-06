# MonitorMyBug - Ant Monitoring System

A Django-based web application for monitoring ant populations and environmental conditions on farms using Raspberry Pi devices.

## Features

### For Farmers
- **User Registration & Authentication**: Secure farmer registration and login system
- **Device Management**: Register and manage multiple Raspberry Pi monitoring devices
- **Real-time Dashboard**: View live sensor data with interactive charts
- **Alert System**: Email notifications when ant counts exceed threshold limits
- **Data Analytics**: Historical data viewing and analysis

### For Raspberry Pi Devices
- **REST API**: Simple API endpoints for data submission
- **Device Authentication**: Secure API key-based authentication
- **Data Submission**: Send sensor data including:
  - Temperature and humidity readings
  - Ant count detection
  - Mealy bug count detection
  - Rainfall and irrigation status

## Installation

### Prerequisites
- Python 3.9+
- Django 4.2+
- SQLite database (included)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MonitorMyBug
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

## Usage

### Web Interface

1. **Access the application**: Navigate to `http://localhost:8000`
2. **Register**: Create a new farmer account at `/register.html`
3. **Login**: Access your dashboard at `/login.html`
4. **Dashboard**: View your devices and sensor data at `/dashboard.html`
5. **Admin**: Access Django admin at `/admin/` (if superuser created)

### API Endpoints

#### Authentication
- `POST /api/register/` - Register new farmer
- `POST /api/login/` - Farmer login

#### Device Management
- `GET /api/devices/` - List farmer's devices
- `POST /api/devices/` - Create new device
- `GET /api/devices/{id}/` - Get device details
- `PUT /api/devices/{id}/` - Update device
- `DELETE /api/devices/{id}/` - Delete device

#### Data Submission (for Raspberry Pi)
- `POST /api/device-data/{device_id}/` - Submit sensor data

#### Dashboard & Analytics
- `GET /api/dashboard/` - Get dashboard summary
- `GET /api/sensor-data/` - Get sensor data with filtering
- `GET /api/alerts/` - Get alert history

### Raspberry Pi Integration

To send data from your Raspberry Pi device:

1. **Register your device** through the web interface
2. **Get your API key** from the device details
3. **Send data** using the following format:

```python
import requests

# Device configuration
DEVICE_ID = "your-device-id"
API_KEY = "your-api-key"
API_URL = "http://your-server.com/api/device-data/{}/".format(DEVICE_ID)

# Sensor data
data = {
    "timestamp": "2024-01-01T12:00:00Z",
    "temperature": 25.5,
    "humidity": 60.2,
    "ant_count": 15,
    "mealy_bugs_count": 3,
    "is_rainfall": False,
    "is_irrigation": True
}

# Send request
headers = {"Authorization": API_KEY}
response = requests.post(API_URL, json=data, headers=headers)
```

## Configuration

### Email Settings

For production, update email settings in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'noreply@monitormybug.com'
```

### Alert Thresholds

Configure ant threshold limits in `settings.py`:

```python
ANT_THRESHOLD_LIMIT = 50  # Default threshold for ant count alerts
```

## Database Models

### Farmer
- Extended user profile with farm information
- Configurable alert thresholds
- Contact information

### Device
- Raspberry Pi device registration
- Unique device ID and API key
- Location and status tracking

### SensorData
- Environmental readings (temperature, humidity)
- Pest counts (ants, mealy bugs)
- Status flags (rainfall, irrigation)
- Automatic alert triggering

### AlertLog
- Record of sent notifications
- Alert type and message tracking
- Timestamp and recipient information

## Security Features

- **Token Authentication**: Secure API access using Django REST framework tokens
- **API Key Protection**: Device-specific API keys for data submission
- **User Permissions**: Role-based access control
- **CORS Configuration**: Configurable cross-origin resource sharing

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface
Access the Django admin interface at `/admin/` to manage:
- Farmers and user accounts
- Devices and their configurations
- Sensor data and alerts
- System settings

## API Documentation

The API follows RESTful conventions and returns JSON responses. All authenticated endpoints require a valid token in the Authorization header:

```
Authorization: Token your-token-here
```

For device data submission, use the device API key:

```
Authorization: your-api-key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
