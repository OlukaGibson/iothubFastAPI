#!/usr/bin/env python3
"""
Test script to verify that device and profile endpoints return config_updated field
"""

import requests
import json

# Base URL - adjust as needed
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_device_profile_config_updated():
    """Test device and profile endpoints for config_updated field"""
    
    print("🧪 Testing Device & Profile endpoints for config_updated field...")
    print("=" * 65)
    
    # You'll need to replace these with actual values
    device_id = 1  # Replace with actual device ID
    profile_id = "1f3e0ddc-acbd-4782-bc39-6805a2df0874"  # Replace with actual profile ID
    
    test_results = []
    
    # Test 1: GET /device/{deviceID}
    print("1️⃣ Testing GET /device/{deviceID}")
    try:
        # You'll need to add proper JWT token authentication headers here
        headers = {
            "Authorization": "Bearer your_jwt_token_here"
        }
        
        response = requests.get(f"{BASE_URL}/device/{device_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            config_data = data.get('config_data', [])
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📄 Found {len(config_data)} config entries")
            
            # Check if config_updated field exists in each config entry
            has_config_updated = True
            for i, config_entry in enumerate(config_data):
                if 'config_updated' not in config_entry:
                    has_config_updated = False
                    print(f"   ❌ Config entry {i} missing config_updated field")
                else:
                    print(f"   ✅ Config entry {i}: config_updated = {config_entry['config_updated']}")
            
            test_results.append(("GET /device/{deviceID}", has_config_updated))
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            test_results.append(("GET /device/{deviceID}", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(("GET /device/{deviceID}", False))
    
    print()
    
    # Test 2: GET /profiles/{profile_id}
    print("2️⃣ Testing GET /profiles/{profile_id}")
    try:
        # You'll need to add proper JWT token authentication headers here
        headers = {
            "Authorization": "Bearer your_jwt_token_here"
        }
        
        response = requests.get(f"{BASE_URL}/profiles/{profile_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            devices = data.get('devices', [])
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📄 Found {len(devices)} devices in profile")
            
            # Check if config_updated field exists in each device's recent_config
            has_config_updated = True
            for i, device in enumerate(devices):
                recent_config = device.get('recent_config', {})
                if 'config_updated' not in recent_config:
                    has_config_updated = False
                    print(f"   ❌ Device {i} ({device.get('name', 'N/A')}) missing config_updated in recent_config")
                else:
                    print(f"   ✅ Device {i} ({device.get('name', 'N/A')}): config_updated = {recent_config['config_updated']}")
            
            test_results.append(("GET /profiles/{profile_id}", has_config_updated))
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            test_results.append(("GET /profiles/{profile_id}", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(("GET /profiles/{profile_id}", False))
    
    print()
    print("📊 SUMMARY")
    print("=" * 65)
    for endpoint, has_field in test_results:
        status = "✅ PASS" if has_field else "❌ FAIL"
        print(f"{status} - {endpoint}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed in test_results if passed)
    print(f"\n🎯 Result: {passed_tests}/{total_tests} endpoints now return config_updated field")

def print_setup_instructions():
    """Print instructions for setting up the test"""
    print("🔧 Setup Instructions:")
    print("=" * 50)
    print("1. Make sure your FastAPI server is running:")
    print("   python server.py")
    print()
    print("2. Get a valid JWT token by logging in:")
    print("   POST /api/v1/login with email and password")
    print("   Copy the returned token")
    print()
    print("3. Update the test variables in this script:")
    print("   - device_id: Valid device ID from your database")
    print("   - profile_id: Valid profile UUID from your database")
    print("   - JWT token in the headers")
    print()
    print("4. Run the test: python test_device_profile_config_updated.py")
    print()

if __name__ == "__main__":
    print_setup_instructions()
    
    # Uncomment the line below after setting up proper test data and JWT token
    # test_device_profile_config_updated()
    
    print("⚠️  Please update the test variables and JWT token first, then uncomment the test call!")