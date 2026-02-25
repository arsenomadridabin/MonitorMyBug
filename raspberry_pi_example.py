#!/usr/bin/env python3
"""
Raspberry Pi Example Script for MonitorMyBug
This script demonstrates how to send sensor data from a Raspberry Pi device
"""

import requests
import json
import random
import time
from datetime import datetime

# Configuration - Replace with your actual values
DEVICE_ID = "raspberry_pi_001"  # Get this from your device registration
API_KEY = "your-api-key-here"   # Get this from your device details
SERVER_URL = "http://localhost:8000"  # Replace with your server URL

def simulate_sensor_data():
    """Simulate sensor readings (replace with actual sensor code)"""
    return {
        "timestamp": datetime.now().isoformat(),
        "temperature": round(random.uniform(20, 35), 1),  # 20-35°C
        "humidity": round(random.uniform(40, 80), 1),     # 40-80%
        "ant_count": random.randint(0, 100),              # 0-100 ants
        "mealy_bugs_count": random.randint(0, 20),        # 0-20 mealy bugs
        "is_rainfall": random.choice([True, False]),      # Random rainfall
        "is_irrigation": random.choice([True, False])     # Random irrigation
    }

def send_sensor_data(sensor_data):
    """Send sensor data to the MonitorMyBug API"""
    url = f"{SERVER_URL}/api/device-data/{DEVICE_ID}/"
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=sensor_data, headers=headers, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            print(f"Data sent successfully - ID: {data['data_id']}")
            return True
        else:
            print(f"Failed to send data: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

def main():
    """Main loop - send data every minute"""
    print("MonitorMyBug Raspberry Pi Client")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Server: {SERVER_URL}")
    print("Sending data every 60 seconds...")
    
    # Validate configuration
    if API_KEY == "your-api-key-here":
        print(" Please update the API_KEY in the script!")
        print("   Get your API key from the device details in the web interface.")
        return
    
    success_count = 0
    error_count = 0
    
    try:
        while True:
            # Get sensor data
            sensor_data = simulate_sensor_data()
            
            print(f"\n📊 Sending data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Temperature: {sensor_data['temperature']}°C")
            print(f"   Humidity: {sensor_data['humidity']}%")
            print(f"   Ant Count: {sensor_data['ant_count']}")
            print(f"   Mealy Bugs: {sensor_data['mealy_bugs_count']}")
            print(f"   Rainfall: {'Yes' if sensor_data['is_rainfall'] else 'No'}")
            print(f"   Irrigation: {'Yes' if sensor_data['is_irrigation'] else 'No'}")
            
            # Send data
            if send_sensor_data(sensor_data):
                success_count += 1
            else:
                error_count += 1
            
            print(f"📈 Stats: {success_count} successful, {error_count} errors")
            
            # Wait 60 seconds before next transmission
            time.sleep(60)
            
    except KeyboardInterrupt:
        print(f"\n\n Stopping client...")
        print(f"Final stats: {success_count} successful, {error_count} errors")

if __name__ == "__main__":
    main()

# Example for actual Raspberry Pi sensors:
"""
# If you have actual sensors connected, replace the simulate_sensor_data() function with:

import board
import adafruit_dht
import adafruit_bh1750

# Initialize sensors
dht = adafruit_dht.DHT22(board.D4)  # Temperature & humidity
light_sensor = adafruit_bh1750.BH1750(board.I2C())  # Light sensor

def get_real_sensor_data():
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        light_level = light_sensor.lux
        
        # Add your ant detection logic here
        ant_count = detect_ants()  # Your ant detection function
        mealy_bugs_count = detect_mealy_bugs()  # Your mealy bug detection function
        
        return {
            "timestamp": datetime.now().isoformat(),
            "temperature": temperature,
            "humidity": humidity,
            "ant_count": ant_count,
            "mealy_bugs_count": mealy_bugs_count,
            "is_rainfall": check_rainfall_sensor(),  # Your rainfall detection
            "is_irrigation": check_irrigation_status()  # Your irrigation status
        }
    except Exception as e:
        print(f"Sensor error: {e}")
        return None
"""
