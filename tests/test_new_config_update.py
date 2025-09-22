#!/usr/bin/env python3
"""
Test script to verify the new config_update endpoint behavior
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_config_update_endpoint():
    """Test the new config_update endpoint behavior"""
    
    # Test parameters
    org_token = "McAzb5kazwe92ToKkmcV_A"
    device_id = 1  # You may need to adjust this based on your test data
    
    url = f"{BASE_URL}/config_update"
    
    print(f"Testing new config_update endpoint: {url}")
    print(f"Parameters: org_token={org_token}, deviceID={device_id}")
    
    try:
        response = requests.get(url, params={
            "org_token": org_token,
            "deviceID": device_id
        })
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            config_updated = data.get('config_updated', None)
            print(f"\n📊 config_updated field: {config_updated}")
            
            if config_updated == False:
                print("✅ config_updated=False: Should return full configuration data")
                if 'configs' in data:
                    print(f"   ✅ Found 'configs' field with {len(data['configs'])} items")
                else:
                    print("   ❌ Missing 'configs' field")
                    
            elif config_updated == True:
                print("✅ config_updated=True: Should return just updated status")
                if 'message' in data:
                    print(f"   ✅ Found message: {data['message']}")
                else:
                    print("   ❌ Missing 'message' field")
                    
            else:
                print(f"❌ Unexpected config_updated value: {config_updated}")
                
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing new config_update endpoint behavior...")
    test_config_update_endpoint()