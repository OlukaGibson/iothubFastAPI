#!/usr/bin/env python3
"""
Test script to verify that all config endpoints now return config_updated boolean
"""

import requests
import json

# Base URL - adjust as needed
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_config_endpoints():
    """Test all config endpoints to verify they return config_updated field"""
    
    print("🧪 Testing all config endpoints for config_updated field...")
    print("=" * 60)
    
    # You'll need to replace these with actual values from your database
    device_id = 1  # Replace with actual device ID
    org_token = "your_org_token_here"  # Get from organisations table
    network_id = "your_network_id"  # Replace with actual network ID
    device_token = "device_token"  # Replace with actual device token
    
    test_results = []
    
    # Test 1: GET /config/{deviceID}
    print("1️⃣ Testing GET /config/{deviceID}")
    try:
        response = requests.get(f"{BASE_URL}/config/{device_id}")
        if response.status_code == 200:
            data = response.json()
            has_config_updated = "config_updated" in data
            print(f"   ✅ Status: {response.status_code}")
            print(f"   {'✅' if has_config_updated else '❌'} config_updated field: {data.get('config_updated', 'MISSING')}")
            test_results.append(("GET /config/{deviceID}", has_config_updated))
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            test_results.append(("GET /config/{deviceID}", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(("GET /config/{deviceID}", False))
    
    print()
    
    # Test 2: POST /config/update
    print("2️⃣ Testing POST /config/update")
    try:
        payload = {
            "deviceID": device_id,
            "configs": {
                "config1": "test_value_1"
            }
        }
        response = requests.post(f"{BASE_URL}/config/update", json=payload)
        if response.status_code == 200:
            data = response.json()
            has_config_updated = "config_updated" in data
            print(f"   ✅ Status: {response.status_code}")
            print(f"   {'✅' if has_config_updated else '❌'} config_updated field: {data.get('config_updated', 'MISSING')}")
            test_results.append(("POST /config/update", has_config_updated))
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            test_results.append(("POST /config/update", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(("POST /config/update", False))
    
    print()
    
    # Test 3: POST /config/mass_edit
    print("3️⃣ Testing POST /config/mass_edit")
    try:
        payload = {
            "device_ids": [device_id],
            "config_values": {
                "config1": "mass_edit_value"
            }
        }
        response = requests.post(f"{BASE_URL}/config/mass_edit", json=payload)
        if response.status_code == 200:
            data = response.json()
            # Check if success array contains objects with config_updated
            success_items = data.get('success', [])
            has_config_updated = False
            if success_items and len(success_items) > 0:
                first_success = success_items[0]
                if isinstance(first_success, dict):
                    has_config_updated = "config_updated" in first_success
            print(f"   ✅ Status: {response.status_code}")
            print(f"   {'✅' if has_config_updated else '❌'} config_updated field in success items: {has_config_updated}")
            test_results.append(("POST /config/mass_edit", has_config_updated))
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            test_results.append(("POST /config/mass_edit", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(("POST /config/mass_edit", False))
    
    print()
    
    # Test 4: GET /config_update
    print("4️⃣ Testing GET /config_update")
    try:
        response = requests.get(f"{BASE_URL}/config_update", params={
            "org_token": org_token,
            "deviceID": device_id
        })
        if response.status_code == 200:
            data = response.json()
            has_config_updated = "config_updated" in data
            print(f"   ✅ Status: {response.status_code}")
            print(f"   {'✅' if has_config_updated else '❌'} config_updated field: {data.get('config_updated', 'MISSING')}")
            test_results.append(("GET /config_update", has_config_updated))
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            test_results.append(("GET /config_update", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(("GET /config_update", False))
    
    print()
    
    # Test 5: GET /network/selfconfig
    print("5️⃣ Testing GET /network/selfconfig")
    try:
        response = requests.get(f"{BASE_URL}/network/selfconfig", params={
            "org_token": org_token,
            "networkID": network_id
        })
        if response.status_code == 200:
            data = response.json()
            has_config_updated = "config_updated" in data
            print(f"   ✅ Status: {response.status_code}")
            print(f"   {'✅' if has_config_updated else '❌'} config_updated field: {data.get('config_updated', 'MISSING')}")
            test_results.append(("GET /network/selfconfig", has_config_updated))
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            test_results.append(("GET /network/selfconfig", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(("GET /network/selfconfig", False))
    
    print()
    print("📊 SUMMARY")
    print("=" * 60)
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
    print("2. Update the test variables in this script:")
    print("   - device_id: Valid device ID from your database")
    print("   - org_token: Valid org token from organisations table")
    print("   - network_id: Valid network ID for the device")
    print("   - device_token: Valid device token for self-config")
    print()
    print("3. Run the test: python test_config_updated_endpoints.py")
    print()

if __name__ == "__main__":
    print_setup_instructions()
    
    # Uncomment the line below after setting up proper test data
    # test_config_endpoints()
    
    print("⚠️  Please update the test variables first, then uncomment the test call!")