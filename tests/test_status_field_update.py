#!/usr/bin/env python3
"""
Test script to verify the updated API endpoints now include the status field
with config_updated, fileDownloadState, and firmwareDownloadState
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ORG_TOKEN = "McAzb5kazwe92ToKkmcV_A"
NETWORK_ID = "8944501905220512557"
DEVICE_ID = 2

def test_selfconfig_endpoint():
    """Test the /network/selfconfig endpoint for status field"""
    print("🧪 Testing /network/selfconfig endpoint...")
    
    url = f"{BASE_URL}/network/selfconfig"
    params = {
        "org_token": ORG_TOKEN,
        "networkID": NETWORK_ID
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received successfully!")
            print(f"📋 Response Keys: {list(data.keys())}")
            
            # Check if status field exists
            if "status" in data:
                print("✅ Status field found!")
                status = data["status"]
                print(f"🔍 Status structure: {json.dumps(status, indent=2)}")
                
                # Verify required status fields
                required_fields = ["config_updated", "fileDownloadState", "firmwareDownloadState"]
                for field in required_fields:
                    if field in status:
                        print(f"✅ {field}: {status[field]}")
                    else:
                        print(f"❌ Missing field: {field}")
            else:
                print("❌ Status field not found in response")
                
            print(f"📄 Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_config_update_endpoint():
    """Test the /config_update endpoint for status field"""
    print("\n🧪 Testing /config_update endpoint...")
    
    url = f"{BASE_URL}/config_update"
    params = {
        "org_token": ORG_TOKEN,
        "deviceID": DEVICE_ID
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received successfully!")
            print(f"📋 Response Keys: {list(data.keys())}")
            
            # Check if status field exists
            if "status" in data:
                print("✅ Status field found!")
                status = data["status"]
                print(f"🔍 Status structure: {json.dumps(status, indent=2)}")
                
                # Verify required status fields
                required_fields = ["config_updated", "fileDownloadState", "firmwareDownloadState"]
                for field in required_fields:
                    if field in status:
                        print(f"✅ {field}: {status[field]}")
                    else:
                        print(f"❌ Missing field: {field}")
            else:
                print("❌ Status field not found in response")
                
            print(f"📄 Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Status Field Implementation")
    print("=" * 50)
    
    print("\n📝 Testing endpoints:")
    print(f"   • /network/selfconfig?org_token={ORG_TOKEN}&networkID={NETWORK_ID}")
    print(f"   • /config_update?org_token={ORG_TOKEN}&deviceID={DEVICE_ID}")
    
    print("\n🎯 Expected status structure:")
    expected_status = {
        "config_updated": "boolean (from ConfigValues)",
        "fileDownloadState": "boolean (from Devices)",
        "firmwareDownloadState": "string enum (from Devices)"
    }
    print(json.dumps(expected_status, indent=2))
    
    print("\n" + "=" * 50)
    
    # Test both endpoints
    test_selfconfig_endpoint()
    test_config_update_endpoint()
    
    print("\n" + "=" * 50)
    print("✨ Testing completed!")

if __name__ == "__main__":
    main()