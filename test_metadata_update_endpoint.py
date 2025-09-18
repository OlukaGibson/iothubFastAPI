#!/usr/bin/env python3
"""
Test script to verify the updated /api/v1/metadata/update endpoint
Now uses GET method with org_token and deviceID query parameters
and includes status field information
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ORG_TOKEN = "McAzb5kazwe92ToKkmcV_A"
DEVICE_ID = 2

def test_metadata_update_endpoint():
    """Test the /metadata/update endpoint with new GET structure"""
    print("🧪 Testing /metadata/update endpoint...")
    
    url = f"{BASE_URL}/metadata/update"
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
            
            # Check metadata field
            if "metadata" in data:
                print("✅ Metadata field found!")
                metadata = data["metadata"]
                if metadata:
                    print(f"📊 Metadata entries: {len(metadata)}")
                    print(f"🔧 Metadata keys: {list(metadata.keys())}")
                else:
                    print("📝 No metadata entries found")
            else:
                print("❌ Metadata field not found in response")
                
            print(f"📄 Full response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Metadata Update Endpoint Changes")
    print("=" * 50)
    
    print(f"\n📝 Testing endpoint: GET /metadata/update")
    print(f"   Parameters:")
    print(f"   • org_token: {ORG_TOKEN}")
    print(f"   • deviceID: {DEVICE_ID}")
    
    print("\n🎯 Expected response structure:")
    expected_response = {
        "deviceID": "integer",
        "status": {
            "config_updated": "boolean (from ConfigValues)",
            "fileDownloadState": "boolean (from Devices)",
            "firmwareDownloadState": "string enum (from Devices)"
        },
        "metadata": {
            "metadata1": "value or null",
            "metadata2": "value or null",
            "...": "..."
        },
        "created_at": "timestamp or null"
    }
    print(json.dumps(expected_response, indent=2))
    
    print("\n" + "=" * 50)
    
    # Test the endpoint
    test_metadata_update_endpoint()
    
    print("\n" + "=" * 50)
    print("✨ Testing completed!")
    
    print("\n📋 Changes Summary:")
    print("• Changed from POST to GET request")
    print("• Uses org_token and deviceID query parameters")
    print("• No longer requires JWT authentication")
    print("• Includes status field with device state information")
    print("• Returns metadata data along with status")

if __name__ == "__main__":
    main()