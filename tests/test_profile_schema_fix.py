#!/usr/bin/env python3
"""
Quick test to verify the profile schema fix works
"""

from schemas.profile import DeviceConfigSummary

def test_device_config_summary_schema():
    """Test that DeviceConfigSummary can handle config_updated boolean"""
    
    print("🧪 Testing DeviceConfigSummary schema with config_updated boolean...")
    
    # Test data similar to what the controller would create
    test_data = {
        "name": "test_device",
        "deviceID": "123",
        "recent_config": {
            "config_updated": True,  # Boolean value
            "config1": "sample_rate_5s",  # String value
            "config2": "post_interval_60s"  # String value
        }
    }
    
    try:
        # This should work now with the Union type
        device_summary = DeviceConfigSummary(**test_data)
        print("✅ Schema validation successful!")
        print(f"   Device: {device_summary.name}")
        print(f"   DeviceID: {device_summary.deviceID}")
        print(f"   Config Updated: {device_summary.recent_config['config_updated']}")
        print(f"   Config1: {device_summary.recent_config['config1']}")
        print(f"   Config2: {device_summary.recent_config['config2']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases for the schema"""
    
    print("\n🧪 Testing edge cases...")
    
    test_cases = [
        {
            "name": "Empty config",
            "data": {
                "name": "test_device",
                "deviceID": "123",
                "recent_config": {}
            }
        },
        {
            "name": "Only config_updated",
            "data": {
                "name": "test_device", 
                "deviceID": "123",
                "recent_config": {
                    "config_updated": False
                }
            }
        },
        {
            "name": "Mixed types",
            "data": {
                "name": "test_device",
                "deviceID": "123", 
                "recent_config": {
                    "config_updated": True,
                    "config1": "string_value",
                    "config2": None,
                    "config3": "another_string"
                }
            }
        }
    ]
    
    for test_case in test_cases:
        try:
            device_summary = DeviceConfigSummary(**test_case["data"])
            print(f"✅ {test_case['name']}: PASS")
        except Exception as e:
            print(f"❌ {test_case['name']}: FAIL - {e}")

if __name__ == "__main__":
    print("🔧 Testing Profile Schema Fix")
    print("=" * 40)
    
    success = test_device_config_summary_schema()
    test_edge_cases()
    
    print(f"\n🎯 Schema fix {'successful' if success else 'failed'}!")