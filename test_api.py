#!/usr/bin/env python3
"""
Test script for MonitorMyBug API
This script demonstrates how to use the API endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def test_farmer_registration():
    """Test farmer registration"""
    print("Testing farmer registration...")
    
    registration_data = {
        "username": "test_farmer",
        "email": "farmer@example.com",
        "password": "testpassword123",
        "password_confirm": "testpassword123",
        "farm_name": "Test Farm",
        "farm_location": "Test Location",
        "phone_number": "+1234567890",
        "ant_threshold_limit": 30
    }
    
    response = requests.post(f"{BASE_URL}/register/", json=registration_data)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Registration successful! Token: {data['token'][:20]}...")
        return data['token']
    else:
        print(f"❌ Registration failed: {response.text}")
        return None

def test_farmer_login():
    """Test farmer login"""
    print("\nTesting farmer login...")
    
    login_data = {
        "username": "test_farmer",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful! Token: {data['token'][:20]}...")
        return data['token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_device_creation(token):
    """Test device creation"""
    print("\nTesting device creation...")
    
    device_data = {
        "device_id": "raspberry_pi_001",
        "device_name": "Farm Monitor #1",
        "location": "North Field"
    }
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.post(f"{BASE_URL}/devices/", json=device_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Device created successfully!")
        print(f"   Device ID: {data['device_id']}")
        print(f"   API Key: {data['api_key'][:20]}...")
        return data
    else:
        print(f"❌ Device creation failed: {response.text}")
        return None

def test_device_data_submission(device_id, api_key):
    """Test device data submission"""
    print("\nTesting device data submission...")
    
    sensor_data = {
        "timestamp": datetime.now().isoformat(),
        "temperature": 25.5,
        "humidity": 65.2,
        "ant_count": 75,  # This should trigger an alert (threshold is 30)
        "mealy_bugs_count": 5,
        "is_rainfall": False,
        "is_irrigation": True
    }
    
    headers = {"Authorization": api_key}
    response = requests.post(f"{BASE_URL}/device-data/{device_id}/", json=sensor_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Data submitted successfully!")
        print(f"   Data ID: {data['data_id']}")
        print(f"   Timestamp: {data['timestamp']}")
        return True
    else:
        print(f"❌ Data submission failed: {response.text}")
        return False

def test_dashboard(token):
    """Test dashboard data retrieval"""
    print("\nTesting dashboard data retrieval...")
    
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Dashboard data retrieved successfully!")
        print(f"   Total devices: {data['summary']['total_devices']}")
        print(f"   Active devices: {data['summary']['active_devices']}")
        print(f"   Recent alerts: {data['summary']['recent_alerts']}")
        return True
    else:
        print(f"❌ Dashboard data retrieval failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("🚀 MonitorMyBug API Test Suite")
    print("=" * 50)
    
    # Test farmer registration
    token = test_farmer_registration()
    if not token:
        print("\n❌ Cannot proceed without valid token")
        return
    
    # Test farmer login
    login_token = test_farmer_login()
    if not login_token:
        print("\n❌ Login test failed")
        return
    
    # Test device creation
    device = test_device_creation(token)
    if not device:
        print("\n❌ Cannot proceed without device")
        return
    
    # Test data submission
    success = test_device_data_submission(device['device_id'], device['api_key'])
    if not success:
        print("\n❌ Data submission test failed")
        return
    
    # Test dashboard
    test_dashboard(token)
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\n📱 Web Interface:")
    print("   Login: http://localhost:8000/login.html")
    print("   Register: http://localhost:8000/register.html")
    print("   Dashboard: http://localhost:8000/dashboard.html")
    print("\n🔧 Admin Interface:")
    print("   Admin: http://localhost:8000/admin/")
    print("   Username: admin")
    print("   Password: admin123")

if __name__ == "__main__":
    main()
