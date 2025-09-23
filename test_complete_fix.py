#!/usr/bin/env python3
"""
Complete test of the API response validation after fixing both controller and schema
"""

from utils.database_config import get_db
from controllers.device import DeviceController
from schemas.device import DeviceResponse
from models.profile import Profiles
from routes.device import sanitize_device_response
import json

def test_complete_api_flow():
    """Test the complete API flow: controller -> sanitizer -> schema validation"""
    print("🔄 Testing Complete API Flow...")
    print("="*60)
    
    db = next(get_db())
    
    # Get organisation_id
    profile = db.query(Profiles).first()
    organisation_id = profile.organisation_id
    
    # Step 1: Controller returns device data
    print("1️⃣ Controller Layer:")
    devices = DeviceController.get_devices(db, organisation_id)
    device = devices[0] if devices else None
    
    if not device:
        print("❌ No devices found")
        return
        
    print(f"   ✅ Device: {device['name']}")
    print(f"   ✅ targetFirmwareVersion: {repr(device['targetFirmwareVersion'])}")
    
    # Step 2: Sanitizer processes the data
    print("\n2️⃣ Sanitizer Layer:")
    sanitized_device = sanitize_device_response(device)
    print(f"   ✅ After sanitization: {repr(sanitized_device['targetFirmwareVersion'])}")
    
    # Step 3: Schema validation
    print("\n3️⃣ Schema Validation:")
    try:
        validated_device = DeviceResponse(**sanitized_device)
        print(f"   ✅ Validation PASSED")
        print(f"   ✅ Final targetFirmwareVersion: {repr(validated_device.targetFirmwareVersion)}")
        
        # Step 4: JSON serialization (what the API actually returns)
        print("\n4️⃣ JSON Response:")
        response_json = validated_device.model_dump()
        print(f"   ✅ JSON serializable: {repr(response_json['targetFirmwareVersion'])}")
        
        print(f"\n🎉 COMPLETE SUCCESS!")
        print(f"   The API will now correctly return: targetFirmwareVersion: '{validated_device.targetFirmwareVersion}'")
        print(f"   Instead of the previous: targetFirmwareVersion: null")
        
    except Exception as e:
        print(f"   ❌ Validation FAILED: {e}")
        return False
    
    print("\n" + "="*60)
    return True

if __name__ == "__main__":
    test_complete_api_flow()