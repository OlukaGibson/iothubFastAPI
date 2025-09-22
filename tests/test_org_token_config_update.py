#!/usr/bin/env python3
"""
Test script for the new org_token-based config update endpoint
/api/v1/device_data/config/{org_token}/{deviceID}/update
"""

import requests
import json

# Base URL - adjust as needed
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_org_token_config_update():
    """Test the new org token config update endpoint"""
    
    print("🧪 Testing org_token config update endpoint...")
    print("=" * 50)
    
    # You'll need to replace these with actual values from your database
    org_token = "your_org_token_here"  # Get from organisations table
    device_id = 1  # Replace with actual device ID
    
    # Test endpoint
    endpoint = f"{BASE_URL}/config/{org_token}/{device_id}/update"
    
    # Test data - updating some config values
    test_configs = {
        "config1": "new_value_1",
        "config2": "new_value_2",
        "config3": "updated_setting"
    }
    
    print(f"📡 POST {endpoint}")
    print(f"📝 Config data: {json.dumps(test_configs, indent=2)}")
    print()
    
    try:
        response = requests.post(endpoint, json=test_configs)
        
        print(f"🔄 Response Status: {response.status_code}")
        print(f"📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success! Checking response structure...")
            
            # Verify expected fields
            expected_fields = ["deviceID", "fileDownloadState", "config_updated", "configs"]
            for field in expected_fields:
                if field in result:
                    print(f"✓ {field}: {result[field]}")
                else:
                    print(f"❌ Missing field: {field}")
            
            # Check config_updated is True
            if result.get("config_updated") is True:
                print("✅ config_updated is correctly set to True")
            else:
                print(f"❌ config_updated should be True, got: {result.get('config_updated')}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def print_setup_instructions():
    """Print instructions for setting up the test"""
    print("🔧 Setup Instructions:")
    print("=" * 50)
    print("1. Make sure your FastAPI server is running:")
    print("   python server.py")
    print()
    print("2. Get a valid org_token from your database:")
    print("   SELECT token FROM organisations WHERE is_active = true LIMIT 1;")
    print()
    print("3. Get a valid device ID that belongs to that organization:")
    print("   SELECT d.deviceID FROM devices d")
    print("   JOIN profiles p ON d.profile = p.id") 
    print("   WHERE p.organisation_id = (SELECT id FROM organisations WHERE token = 'your_org_token');")
    print()
    print("4. Update the org_token and device_id variables in this script")
    print("5. Run the test: python test_org_token_config_update.py")
    print()

if __name__ == "__main__":
    print_setup_instructions()
    
    # Uncomment the line below after setting up proper org_token and device_id
    # test_org_token_config_update()
    
    print("⚠️  Please set up the org_token and device_id first, then uncomment the test call!")