#!/usr/bin/env python3
"""
Direct test of the device controller fix for targetFirmwareVersion bug
"""

from utils.database_config import get_db
from controllers.device import DeviceController
from models.device import Devices
from models.profile import Profiles
import json

def test_target_firmware_version():
    """Test that targetFirmwareVersion returns the correct firmware version string"""
    print("🔍 Testing targetFirmwareVersion fix...")
    
    db = next(get_db())
    
    # Get the first profile to use its organisation_id
    profile = db.query(Profiles).first()
    if not profile:
        print("❌ No profiles found in database")
        return
    
    organisation_id = profile.organisation_id
    print(f"✅ Using organisation_id: {organisation_id}")
    
    # Get devices using the controller (this simulates the API endpoint)
    devices = DeviceController.get_devices(db, organisation_id)
    
    if not devices:
        print("❌ No devices found")
        return
    
    print(f"✅ Found {len(devices)} device(s)")
    
    # Check each device
    for i, device in enumerate(devices):
        print(f"\n📱 Device {i+1}: {device['name']}")
        print(f"   deviceID: {device['deviceID']}")
        
        # This is the key test - check if targetFirmwareVersion is properly populated
        target_fw = device['targetFirmwareVersion']
        print(f"   targetFirmwareVersion: {repr(target_fw)}")
        
        if target_fw is None:
            print("   ❌ STILL NULL - The fix didn't work")
        elif isinstance(target_fw, str) and target_fw:
            print(f"   ✅ SUCCESS - Returns firmware version string: '{target_fw}'")
        else:
            print(f"   ⚠️  UNEXPECTED - Got type {type(target_fw)}: {target_fw}")
        
        # Also check the raw database value for comparison
        raw_device = db.query(Devices).filter_by(deviceID=device['deviceID']).first()
        if raw_device:
            print(f"   Raw DB targetFirmwareVersion: {raw_device.targetFirmwareVersion}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_target_firmware_version()