#!/usr/bin/env python3
"""
Test script to verify config_updated is set to true after selfconfig call
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_config_updated_behavior():
    """Test that config_updated is set to true after selfconfig endpoint is called"""
    
    # Test parameters
    org_token = "McAzb5kazwe92ToKkmcV_A"
    network_id = "8944501905220512557"
    
    url = f"{BASE_URL}/network/selfconfig"
    
    print(f"Testing config_updated behavior at: {url}")
    print(f"Parameters: org_token={org_token}, networkID={network_id}")
    
    try:
        response = requests.get(url, params={
            "org_token": org_token,
            "networkID": network_id
        })
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            config_updated = data.get('config_updated', None)
            print(f"\n✅ config_updated field: {config_updated}")
            
            if config_updated is True:
                print("✅ SUCCESS: config_updated is set to True as expected!")
            elif config_updated is False:
                print("❌ ISSUE: config_updated is still False")
            else:
                print(f"❌ UNEXPECTED: config_updated has unexpected value: {config_updated}")
                
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing config_updated behavior...")
    test_config_updated_behavior()