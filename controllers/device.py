import random
import string
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.device import Devices
from models.firmware import Firmware
from models.profile import Profiles
from models.devicedata_value import DeviceData
from models.config_value import ConfigValues
from models.metadata_value import MetadataValues
from schemas.status import DeviceStatus, FirmwareDownload
import uuid
from datetime import datetime
from fastapi import HTTPException

class DeviceController:
    @staticmethod
    def build_device_status(db: Session, device: Devices, latest_config) -> dict:
        """Build standardized status structure for device responses"""
        # Get firmware information for the target firmware version
        firmware_version = "unknown"
        firmware_crc = "0x00000000"
        firmware_bin_size = 0
        
        if device.targetFirmwareVersion:
            firmware = db.query(Firmware).filter_by(id=device.targetFirmwareVersion).first()
            if firmware:
                firmware_version = firmware.firmware_version
                firmware_crc = firmware.crc32 or "0x00000000"
                firmware_bin_size = firmware.firmware_bin_size
        
        return {
            "config_updated": latest_config.config_updated if latest_config else False,
            "fileDownloadState": device.fileDownloadState,
            "firmwareDownload": {
                "firmwareDownloadState": device.firmwareDownloadState,
                "version": firmware_version,
                "fwcrc": firmware_crc,
                "firmware_size": firmware_bin_size
            }
        }

    @staticmethod
    def create_device(db: Session, organisation_id, device_data):
        # Check for duplicate name, readkey, writekey, deviceID
        if db.query(Devices).filter_by(name=device_data.name).first():
            raise HTTPException(status_code=400, detail=f"Device name '{device_data.name}' already exists.")
        # Optionally check for readkey/writekey uniqueness if you allow custom keys
        # if db.query(Devices).filter_by(readkey=device_data.readkey).first():
        #     raise HTTPException(status_code=400, detail="Device readkey already exists.")
        # if db.query(Devices).filter_by(writekey=device_data.writekey).first():
        #     raise HTTPException(status_code=400, detail="Device writekey already exists.")

        # Generate random keys
        writekey = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        readkey = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        # Get next deviceID
        last_device = db.query(Devices).order_by(Devices.deviceID.desc()).first()
        deviceID = (last_device.deviceID + 1) if last_device else 1

        # Check for duplicate deviceID (should not happen, but for safety)
        if db.query(Devices).filter_by(deviceID=deviceID).first():
            raise HTTPException(status_code=400, detail=f"DeviceID '{deviceID}' already exists.")

        # Validate that the profile belongs to the user's organization
        profile = db.query(Profiles).filter_by(id=device_data.profile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found.")
        if str(profile.organisation_id) != str(organisation_id):
            raise HTTPException(status_code=403, detail="Profile does not belong to your organization.")

        new_device = Devices(
            name=device_data.name,
            readkey=readkey,
            writekey=writekey,
            deviceID=deviceID,
            networkID=device_data.networkID,
            currentFirmwareVersion=device_data.currentFirmwareVersion,
            previousFirmwareVersion=device_data.previousFirmwareVersion,
            targetFirmwareVersion=device_data.targetFirmwareVersion,
            fileDownloadState=device_data.fileDownloadState,
            profile=device_data.profile,
            firmwareDownloadState=device_data.firmwareDownloadState
        )
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        # Return the ORM object for FastAPI response serialization
        return new_device

    @staticmethod
    def get_devices(db: Session, organisation_id):
        # Get devices that belong to profiles in the user's organization
        devices = db.query(Devices).join(Profiles).filter(Profiles.organisation_id == organisation_id).all()
        devices_list = []
        for device in devices:
            currentFirmware = db.query(Firmware).filter_by(id=device.currentFirmwareVersion).first()
            previousFirmware = db.query(Firmware).filter_by(id=device.previousFirmwareVersion).first()
            targetFirmware = db.query(Firmware).filter_by(id=device.targetFirmwareVersion).first()
            currentFirmwareVersion = currentFirmware.firmware_version if currentFirmware else None
            previousFirmwareVersion = previousFirmware.firmware_version if previousFirmware else currentFirmwareVersion
            targetFirmwareVersion = targetFirmware.firmware_version if targetFirmware else currentFirmwareVersion
            profile = db.query(Profiles).filter_by(id=device.profile).first()
            profile_name = profile.name if profile else None
            last_metadata_entry = db.query(DeviceData).filter_by(deviceID=device.deviceID).order_by(DeviceData.created_at.desc()).first()
            last_posted_time = last_metadata_entry.created_at if last_metadata_entry else None
            device_dict = {
                'id': device.id,
                'name': device.name,
                'readkey': device.readkey,
                'writekey': device.writekey,
                'deviceID': device.deviceID,
                'networkID': device.networkID,
                'currentFirmwareVersion': currentFirmwareVersion,
                'previousFirmwareVersion': previousFirmwareVersion,
                'targetFirmwareVersion': targetFirmwareVersion,
                'fileDownloadState': device.fileDownloadState,
                'profile': device.profile,
                'profile_name': profile_name,
                'last_posted_time': last_posted_time,
                'created_at': device.created_at,
                'firmwareDownloadState': device.firmwareDownloadState,
            }
            devices_list.append(device_dict)
        return devices_list

    @staticmethod
    def get_device(db: Session, organisation_id, deviceID):
        device = db.query(Devices).join(Profiles).filter(
            Devices.deviceID == deviceID,
            Profiles.organisation_id == organisation_id
        ).first()
        if not device:
            return {'message': 'Device not found!'}, 404
        currentFirmware = db.query(Firmware).filter_by(id=device.currentFirmwareVersion).first()
        previousFirmware = db.query(Firmware).filter_by(id=device.previousFirmwareVersion).first()
        targetFirmware = db.query(Firmware).filter_by(id=device.targetFirmwareVersion).first()
        currentFirmwareVersion = currentFirmware.firmware_version if currentFirmware else None
        previousFirmwareVersion = previousFirmware.firmware_version if previousFirmware else None
        targetFirmwareVersion = targetFirmware.firmware_version if targetFirmware else None
        deviceProfile = db.query(Profiles).filter_by(id=device.profile).first()
        
        # Get field name mappings from profile
        field_names = {}
        config_names = {}
        metadata_names = {}
        
        if deviceProfile:
            for i in range(1, 16):
                field_val = getattr(deviceProfile, f'field{i}', None)
                if field_val:
                    field_names[f'field{i}'] = field_val
                metadata_val = getattr(deviceProfile, f'metadata{i}', None)
                if metadata_val:
                    metadata_names[f'metadata{i}'] = metadata_val
            
            for i in range(1, 11):
                config_val = getattr(deviceProfile, f'config{i}', None)
                if config_val:
                    config_names[f'config{i}'] = config_val
        
        device_data = db.query(DeviceData).filter_by(deviceID=deviceID).order_by(DeviceData.created_at.desc()).limit(100).all()
        config_data = db.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).limit(100).all()
        meta_data = db.query(MetadataValues).filter_by(deviceID=deviceID).order_by(MetadataValues.created_at.desc()).limit(100).all()
        device_data_list = []
        config_data_list = []
        meta_data_list = []
        for data in meta_data:
            data_dict = {
                'entryID': data.id,
                'created_at': data.created_at,
            }
            for i in range(1, 16):
                val = getattr(data, f'metadata{i}', None)
                if val:
                    data_dict[f'metadata{i}'] = val
            meta_data_list.append(data_dict)
        for data in config_data:
            data_dict = {
                'entryID': data.id,
                'created_at': data.created_at,
                'config_updated': data.config_updated,
            }
            for i in range(1, 11):
                val = getattr(data, f'config{i}', None)
                if val:
                    data_dict[f'config{i}'] = val
            config_data_list.append(data_dict)
        for data in device_data:
            data_dict = {
                'entryID': data.id,
                'created_at': data.created_at,
            }
            for i in range(1, 16):
                val = getattr(data, f'field{i}', None)
                if val:
                    data_dict[f'field{i}'] = val
            device_data_list.append(data_dict)
        device_dict = {
            'id': device.id,
            'created_at': device.created_at,
            'name': device.name,
            'readkey': device.readkey,
            'writekey': device.writekey,
            'deviceID': device.deviceID,
            'profile': device.profile,
            'profile_name': deviceProfile.name if deviceProfile else None,
            'currentFirmwareVersion': currentFirmwareVersion,
            'targetFirmwareVersion': targetFirmwareVersion,
            'previousFirmwareVersion': previousFirmwareVersion,
            'networkID': device.networkID,
            'fileDownloadState': device.fileDownloadState,
            'firmwareDownloadState': device.firmwareDownloadState,
            'device_data': device_data_list,
            'config_data': config_data_list,
            'meta_data': meta_data_list,
            'field_names': field_names,
            'config_names': config_names,
            'metadata_names': metadata_names
        }
        return device_dict

    @staticmethod
    def update_device(db: Session, organisation_id, deviceID, device_update):
        device = db.query(Devices).join(Profiles).filter(
            Devices.deviceID == deviceID,
            Profiles.organisation_id == organisation_id
        ).first()
        if not device:
            return {'message': 'Device not found!'}, 404
        # Update fields
        device.name = device_update.name or device.name
        device.networkID = device_update.networkID or device.networkID
        device.currentFirmwareVersion = device_update.currentFirmwareVersion or device.currentFirmwareVersion
        device.previousFirmwareVersion = device_update.previousFirmwareVersion or device.previousFirmwareVersion
        device.targetFirmwareVersion = device_update.targetFirmwareVersion or device.targetFirmwareVersion
        device.fileDownloadState = device_update.fileDownloadState if device_update.fileDownloadState is not None else device.fileDownloadState
        device.profile = device_update.profile or device.profile
        device.firmwareDownloadState = device_update.firmwareDownloadState or device.firmwareDownloadState
        db.commit()
        db.refresh(device)
        return {'message': 'Device updated successfully!'}

    @staticmethod
    def update_firmware(db: Session, organisation_id, deviceID, firmwareID, firmwareVersion):
        device = db.query(Devices).join(Profiles).filter(
            Devices.deviceID == deviceID,
            Profiles.organisation_id == organisation_id
        ).first()
        if not device:
            raise HTTPException(status_code=404, detail='Device not found!')
        firmware = db.query(Firmware).filter_by(id=firmwareID, firmware_version=firmwareVersion).first()
        if not firmware:
            raise HTTPException(status_code=404, detail='Firmware not found or version mismatch!')
        device.targetFirmwareVersion = firmwareID
        if device.currentFirmwareVersion == firmwareID:
            device.firmwareDownloadState = 'updated'
        else:
            device.firmwareDownloadState = 'pending'
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def self_config(db: Session, organisation_id, networkID):
        device = db.query(Devices).join(Profiles).filter(
            Devices.networkID == networkID,
            Profiles.organisation_id == organisation_id
        ).first()
        if not device:
            return {'message': 'Device not found!'}, 404
        try:
            profile = db.query(Profiles).filter_by(id=device.profile).first()
            latest_config = db.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by(ConfigValues.created_at.desc()).first()
            
            # Update config_updated to True since device is fetching its configuration
            if latest_config:
                latest_config.config_updated = True
                db.commit()
            
            device_details = {
                'name': device.name,
                'deviceID': device.deviceID,
                'networkID': device.networkID,
                'writekey': device.writekey,
                'readkey': device.readkey,
                'status': DeviceController.build_device_status(db, device, latest_config),
                'configs': {}
            }
            if profile and latest_config:
                for i in range(1, 11):
                    config_name = getattr(profile, f'config{i}', None)
                    if config_name:
                        config_value = getattr(latest_config, f'config{i}', None)
                        device_details['configs'][f'config{i}'] = config_value
            return device_details
        except Exception as e:
            # Rollback any database changes if there's an error
            db.rollback()
            return {'message': 'Device self-configuration failed!', 'error': str(e)}, 500
      