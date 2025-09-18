#!/usr/bin/env python3
"""
Test script to verify the updated /api/v1/metadata_update endpoint
Now accepts metadata1-15 as query parameters, stores them in database,
and returns simple success/failure message with status
"""

import requests
import json
from urllib.parse import urlencode

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ORG_TOKEN = "McAzb5kazwe92ToKkmcV_A"
DEVICE_ID = 2

def test_metadata_update_with_params():
    """Test the /metadata_update endpoint with metadata parameters"""
    print("🧪 Testing /metadata_update endpoint with metadata parameters...")
    
    # Test data - some metadata fields with values, others None
    metadata_params = {
        "org_token": ORG_TOKEN,
        "deviceID": DEVICE_ID,
        "meta1": "Temperature: 25.5°C",
        "meta2": "Humidity: 60%",
        "meta3": "Pressure: 1013.25 hPa",
        "meta5": "Battery: 85%",
        "meta7": "Signal Strength: -65 dBm",
        "meta10": "Location: Building A, Floor 2"
        # meta4, meta6, meta8, meta9, meta11-15 will be None (not included)
    }
    
    url = f"{BASE_URL}/metadata_update"
    
    try:
        response = requests.get(url, params=metadata_params)
        print(f"📡 Status Code: {response.status_code}")
        print(f"🔗 Request URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received successfully!")
            print(f"📋 Response Keys: {list(data.keys())}")
            
            # Check message field
            if "message" in data:
                message = data["message"]
                print(f"📝 Message: {message}")
                
                if message == "success":
                    print("✅ Metadata update successful!")
                else:
                    print(f"❌ Update failed with message: {message}")
                    if "reason" in data:
                        print(f"📄 Reason: {data['reason']}")
            else:
                print("❌ Message field not found in response")
            
            # Check status field
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

def test_metadata_update_with_no_params():
    """Test the /metadata_update endpoint with no metadata parameters (all None)"""
    print("\n🧪 Testing /metadata_update endpoint with no metadata parameters...")
    
    params = {
        "org_token": ORG_TOKEN,
        "deviceID": DEVICE_ID
        # No meta1-meta15 parameters provided
    }
    
    url = f"{BASE_URL}/metadata_update"
    
    try:
        response = requests.get(url, params=params)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received successfully!")
            
            if data.get("message") == "success":
                print("✅ Metadata update successful even with no parameters!")
            else:
                print(f"📝 Message: {data.get('message')}")
                if "reason" in data:
                    print(f"📄 Reason: {data.get('reason')}")
                    
            print(f"📄 Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_invalid_org_token():
    """Test with invalid organization token"""
    print("\n🧪 Testing /metadata_update endpoint with invalid org_token...")
    
    params = {
        "org_token": "INVALID_TOKEN_123",
        "deviceID": DEVICE_ID,
        "meta1": "Test data"
    }
    
    url = f"{BASE_URL}/metadata_update"
    
    try:
        response = requests.get(url, params=params)
        print(f"📡 Status Code: {response.status_code}")
        
        data = response.json()
        print(f"📝 Message: {data.get('message')}")
        if data.get('message') == 'failure':
            print(f"✅ Properly handled invalid token: {data.get('reason')}")
        
        print(f"📄 Response: {json.dumps(data, indent=2)}")
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Updated Metadata Update Endpoint")
    print("=" * 60)
    
    print(f"\n📝 Testing endpoint: GET /metadata_update")
    print(f"   Base parameters:")
    print(f"   • org_token: {ORG_TOKEN}")
    print(f"   • deviceID: {DEVICE_ID}")
    print(f"   • meta1-meta15: Various test values")
    
    print("\n🎯 Expected response structure:")
    expected_response = {
        "message": "success or failure",
        "reason": "only present if failure",
        "status": {
            "config_updated": "boolean",
            "fileDownloadState": "boolean", 
            "firmwareDownloadState": "string enum"
        }
    }
    print(json.dumps(expected_response, indent=2))
    
    print("\n" + "=" * 60)
    
    # Test scenarios
    test_metadata_update_with_params()
    test_metadata_update_with_no_params()
    test_invalid_org_token()
    
    print("\n" + "=" * 60)
    print("✨ Testing completed!")
    
    print("\n📋 Endpoint Features:")
    print("• Accepts metadata1-15 as optional query parameters (meta1-meta15)")
    print("• Validates org_token and device ownership") 
    print("• Stores metadata in database with current timestamp")
    print("• Returns simple success/failure message")
    print("• Always includes status information")
    print("• Handles None values for unused metadata fields")

if __name__ == "__main__":
    main()