#!/usr/bin/env python3
"""
Test script to verify config_updated flag changes after data retrieval
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_config_updated_flag_behavior():
    """Test that config_updated changes from False to True after data retrieval"""
    
    # Test parameters
    org_token = "McAzb5kazwe92ToKkmcV_A"
    device_id = 2  # Based on your example
    
    url = f"{BASE_URL}/config_update"
    params = {
        "org_token": org_token,
        "deviceID": device_id
    }
    
    print(f"Testing config_updated flag behavior at: {url}")
    print(f"Parameters: {params}")
    print("=" * 60)
    
    # First call - should return config_updated=False and full data
    print("1️⃣ FIRST CALL - Expecting config_updated=False with full data:")
    try:
        response1 = requests.get(url, params=params)
        print(f"Status: {response1.status_code}")
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"Response: {json.dumps(data1, indent=2)}")
            
            config_updated_1 = data1.get('config_updated', None)
            has_configs_1 = 'configs' in data1
            
            print(f"\n✅ config_updated: {config_updated_1}")
            print(f"✅ Has configs field: {has_configs_1}")
            
            if config_updated_1 == False and has_configs_1:
                print("✅ SUCCESS: First call returned False with configuration data!")
            else:
                print("❌ UNEXPECTED: First call didn't return expected format")
                
        else:
            print(f"❌ First call failed with status: {response1.status_code}")
            return
            
    except Exception as e:
        print(f"❌ First call error: {e}")
        return
    
    print("\n" + "=" * 60)
    
    # Small delay to ensure any async operations complete
    time.sleep(1)
    
    # Second call - should return config_updated=True with just status
    print("2️⃣ SECOND CALL - Expecting config_updated=True with just status:")
    try:
        response2 = requests.get(url, params=params)
        print(f"Status: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"Response: {json.dumps(data2, indent=2)}")
            
            config_updated_2 = data2.get('config_updated', None)
            has_configs_2 = 'configs' in data2
            has_message_2 = 'message' in data2
            
            print(f"\n✅ config_updated: {config_updated_2}")
            print(f"✅ Has configs field: {has_configs_2}")
            print(f"✅ Has message field: {has_message_2}")
            
            if config_updated_2 == True and not has_configs_2 and has_message_2:
                print("✅ SUCCESS: Second call returned True with status message!")
            else:
                print("❌ UNEXPECTED: Second call didn't return expected format")
                
        else:
            print(f"❌ Second call failed with status: {response2.status_code}")
            
    except Exception as e:
        print(f"❌ Second call error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("  - First call should return config_updated=False with full config data")
    print("  - After first call, database should be updated to config_updated=True")  
    print("  - Second call should return config_updated=True with just status message")

if __name__ == "__main__":
    print("Testing config_updated flag behavior change...")
    test_config_updated_flag_behavior()