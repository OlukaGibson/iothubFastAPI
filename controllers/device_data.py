from sqlalchemy.orm import Session
from models.device import Devices
from models.profile import Profiles
from models.devicedata_value import DeviceData
from models.metadata_value import MetadataValues
from models.config_value import ConfigValues
from models.firmware import Firmware
from schemas.device_data import DeviceDataCreate, MetadataValuesCreate, ConfigValuesCreate
from datetime import datetime, timedelta
from fastapi import HTTPException
import uuid

# Import new status schemas
from schemas.status import DeviceStatus, FirmwareDownload

class DeviceDataController:
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
    def update_device_data(db: Session, writekey: str, fields: dict):
        device = db.query(Devices).filter_by(writekey=writekey).first()
        if not device:
            raise HTTPException(status_code=403, detail="Invalid API key!")
        profile = db.query(Profiles).filter_by(id=device.profile).first()
        field_label = {f'field{i}': getattr(profile, f'field{i}', None) for i in range(1, 16)}
        data_fields = {}
        for i in range(1, 16):
            key = f'field{i}'
            data_fields[key] = fields.get(key) if field_label[key] else None
        entryID = DeviceData.get_next_entry_id(db, device.deviceID)
        new_entry = DeviceData(
            created_at=datetime.now(),
            deviceID=device.deviceID,
            entryID=entryID,
            **data_fields
        )
        db.add(new_entry)
        db.commit()
        return new_entry

    @staticmethod
    def bulk_update(db: Session, deviceID: int, updates: list):
        device = db.query(Devices).filter_by(deviceID=deviceID).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found!")
        for update in updates:
            created_at = update.get('created_at')
            if created_at:
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            else:
                created_at = datetime.now()
            fields = {f'field{i}': update.get(f'field{i}', None) for i in range(1, 16)}
            entryID = DeviceData.get_next_entry_id(db, device.deviceID)
            new_entry = DeviceData(
                deviceID=device.deviceID,
                created_at=created_at,
                entryID=entryID,
                **fields
            )
            db.add(new_entry)
        db.commit()
        return {"message": "success"}

class MetadataValuesController:
    @staticmethod
    def update_metadata(db: Session, writekey: str, metadatas: dict):
        device = db.query(Devices).filter_by(writekey=writekey).first()
        if not device:
            raise HTTPException(status_code=403, detail="Invalid API key!")
        profile = db.query(Profiles).filter_by(id=device.profile).first()
        metadata_label = {f'metadata{i}': getattr(profile, f'metadata{i}', None) for i in range(1, 16)}
        data_metadatas = {}
        for i in range(1, 16):
            key = f'metadata{i}'
            data_metadatas[key] = metadatas.get(key) if metadata_label[key] else None
        new_entry = MetadataValues(
            created_at=datetime.now(),
            deviceID=device.deviceID,
            **data_metadatas
        )
        db.add(new_entry)
        db.commit()
        return new_entry

    @staticmethod
    def get_metadata_update(db: Session, org_token: str, deviceID: int):
        """Get metadata update with status information using org_token and deviceID."""
        try:
            from controllers.user_org import OrganisationController
            
            # Validate org_token and get organisation_id
            organisation_id = OrganisationController.get_organisation_id_by_token(db, org_token)
            if not organisation_id:
                raise HTTPException(status_code=404, detail="Invalid organization token!")
            
            # Get device and verify it belongs to the organization
            device = db.query(Devices).filter_by(deviceID=deviceID).first()
            if not device:
                raise HTTPException(status_code=404, detail="Device not found!")
            
            # Get the device's profile and check if it belongs to the organization
            profile = db.query(Profiles).filter_by(id=device.profile).first()
            if not profile or str(profile.organisation_id) != organisation_id:
                raise HTTPException(status_code=403, detail="Device does not belong to your organization!")
            
            # Get the latest metadata entry
            latest_metadata = db.query(MetadataValues).filter_by(deviceID=deviceID).order_by(MetadataValues.created_at.desc()).first()
            
            # Get the latest config for config_updated status
            latest_config = db.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
            
            # Prepare the response with status information
            metadata_response = {
                "deviceID": deviceID,
                "status": DeviceDataController.build_device_status(db, device, latest_config),
                "metadata": {},
                "created_at": latest_metadata.created_at if latest_metadata else None
            }
            
            # Add metadata values if they exist
            if latest_metadata:
                for i in range(1, 16):
                    metadata_value = getattr(latest_metadata, f'metadata{i}', None)
                    if metadata_value is not None:
                        metadata_response["metadata"][f'metadata{i}'] = metadata_value
            
            return metadata_response
            
        except Exception as e:
            # Rollback any database changes if there's an error
            db.rollback()
            if isinstance(e, HTTPException):
                raise e
            else:
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @staticmethod
    def update_metadata_with_status(db: Session, org_token: str, deviceID: int, metadata_dict: dict):
        """Update device metadata using org_token and deviceID, return simple success/failure message with status."""
        try:
            from controllers.user_org import OrganisationController
            
            # Validate org_token and get organisation_id
            organisation_id = OrganisationController.get_organisation_id_by_token(db, org_token)
            if not organisation_id:
                return {
                    "message": "failure",
                    "reason": "Invalid organization token",
                    "status": {
                        "config_updated": None,
                        "fileDownloadState": None,
                        "firmwareDownload": {
                            "firmwareDownloadState": None,
                            "version": "unknown",
                            "fwcrc": "0x00000000",
                            "firmware_size": 0
                        }
                    }
                }
            
            # Get device and verify it belongs to the organization
            device = db.query(Devices).filter_by(deviceID=deviceID).first()
            if not device:
                return {
                    "message": "failure",
                    "reason": "Device not found",
                    "status": {
                        "config_updated": None,
                        "fileDownloadState": None,
                        "firmwareDownload": {
                            "firmwareDownloadState": None,
                            "version": "unknown",
                            "fwcrc": "0x00000000",
                            "firmware_size": 0
                        }
                    }
                }
            
            # Get the device's profile and check if it belongs to the organization
            profile = db.query(Profiles).filter_by(id=device.profile).first()
            if not profile or str(profile.organisation_id) != organisation_id:
                return {
                    "message": "failure",
                    "reason": "Device does not belong to your organization",
                    "status": {
                        "config_updated": None,
                        "fileDownloadState": None,
                        "firmwareDownload": {
                            "firmwareDownloadState": None,
                            "version": "unknown",
                            "fwcrc": "0x00000000",
                            "firmware_size": 0
                        }
                    }
                }
            
            # Prepare metadata data for storage - only store non-None values
            data_metadata = {}
            for i in range(1, 16):
                key = f'metadata{i}'
                value = metadata_dict.get(key)
                if value is not None:
                    data_metadata[key] = value
                else:
                    data_metadata[key] = None
            
            # Create new metadata entry
            new_entry = MetadataValues(
                created_at=datetime.now(),
                deviceID=device.deviceID,
                **data_metadata
            )
            db.add(new_entry)
            db.commit()
            
            # Get latest config for status
            latest_config = db.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
            
            return {
                "message": "success",
                "status": DeviceDataController.build_device_status(db, device, latest_config)
            }
            
        except Exception as e:
            # Rollback any database changes if there's an error
            db.rollback()
            return {
                "message": "failure",
                "reason": f"Internal server error: {str(e)}",
                "status": {
                    "config_updated": None,
                    "fileDownloadState": None,
                    "firmwareDownload": {
                        "firmwareDownloadState": None,
                        "version": "unknown",
                        "fwcrc": "0x00000000",
                        "firmware_size": 0
                    }
                }
            }

class ConfigValuesController:
    @staticmethod
    def update_config_data(db: Session, deviceID: int, configs: dict):
        device = db.query(Devices).filter_by(deviceID=deviceID).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found!")
        profile = db.query(Profiles).filter_by(id=device.profile).first()
        latest_config = db.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
        config_data = {}
        for i in range(1, 11):
            key = f'config{i}'
            new_value = configs.get(key)
            config_data[key] = new_value if new_value is not None else (getattr(latest_config, key, None) if latest_config else None)
        new_entry = ConfigValues(
            created_at=datetime.now(),
            deviceID=deviceID,
            **config_data
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        # Get latest config for status
        latest_config = db.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by(ConfigValues.created_at.desc()).first()
        
        # Return configuration in same format as get_config_data
        configuration = {
            "deviceID": device.deviceID,
            "fileDownloadState": device.fileDownloadState,
            "status": DeviceDataController.build_device_status(db, device, latest_config),
            "configs": {}
        }
        for i in range(1, 11):
            config_value = getattr(new_entry, f'config{i}', None)
            if config_value is not None:
                configuration["configs"][f'config{i}'] = config_value
        return configuration

    @staticmethod
    def mass_edit_config_data(db: Session, device_ids: list, config_values: dict):
        results = {'success': [], 'failed': []}
        for device_id in device_ids:
            try:
                device = db.query(Devices).filter_by(deviceID=device_id).first()
                if not device:
                    results['failed'].append({'deviceID': device_id, 'error': 'Device not found'})
                    continue
                latest_config = db.query(ConfigValues).filter_by(deviceID=device_id).order_by(ConfigValues.created_at.desc()).first()
                configs = {}
                for i in range(1, 11):
                    key = f'config{i}'
                    new_value = config_values.get(key)
                    if new_value == "":
                        configs[key] = getattr(latest_config, key, None) if latest_config else None
                    else:
                        configs[key] = new_value
                new_config = ConfigValues(
                    created_at=datetime.now(),
                    deviceID=device_id,
                    **configs
                )
                db.add(new_config)
                db.flush()  # Flush to get the new config data
                db.refresh(new_config)
                
                # Get latest config for status
                latest_config = db.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by(ConfigValues.created_at.desc()).first()
                
                # Create config response with status field
                device_config = {
                    "deviceID": device.deviceID,
                    "fileDownloadState": device.fileDownloadState,
                    "status": DeviceDataController.build_device_status(db, device, latest_config),
                    "configs": {}
                }
                for i in range(1, 11):
                    config_value = getattr(new_config, f'config{i}', None)
                    if config_value is not None:
                        device_config["configs"][f'config{i}'] = config_value
                
                results['success'].append(device_config)
            except Exception as e:
                results['failed'].append({'deviceID': device_id, 'error': str(e)})
        db.commit()
        return results

    @staticmethod
    def get_config_data(db: Session, deviceID: int):
        device = db.query(Devices).filter_by(deviceID=deviceID).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found!")
        config_data = db.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
        if not config_data:
            raise HTTPException(status_code=404, detail="No config data found for this device!")
        configuration = {
            "deviceID": device.deviceID,
            "fileDownloadState": device.fileDownloadState,
            "status": DeviceDataController.build_device_status(db, device, config_data),
            "configs": {}
        }
        for i in range(1, 11):
            config_value = getattr(config_data, f'config{i}', None)
            if config_value is not None:
                configuration["configs"][f'config{i}'] = config_value
        return configuration

    @staticmethod
    def update_config_with_org_token(db: Session, org_token: str, deviceID: int, configs: dict = None):
        """Update device config using org_token authentication and return latest config with config_updated=True"""
        from controllers.user_org import OrganisationController
        
        # Validate org_token and get organisation_id
        organisation_id = OrganisationController.get_organisation_id_by_token(db, org_token)
        if not organisation_id:
            raise HTTPException(status_code=404, detail="Invalid organization token!")
        
        # Get device and verify it belongs to the organization
        device = db.query(Devices).filter_by(deviceID=deviceID).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found!")
        
        # Get the device's profile and check if it belongs to the organization
        profile = db.query(Profiles).filter_by(id=device.profile).first()
        if not profile or str(profile.organisation_id) != organisation_id:
            raise HTTPException(status_code=403, detail="Device does not belong to your organization!")
        
        # Get the latest config to preserve existing values
        latest_config = db.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
        
        # Prepare config data, preserving existing values if new ones aren't provided
        config_data = {}
        for i in range(1, 11):
            key = f'config{i}'
            if configs and key in configs:
                config_data[key] = configs[key]
            else:
                config_data[key] = getattr(latest_config, key, None) if latest_config else None
        
        # Create new config entry with config_updated=True
        new_config = ConfigValues(
            created_at=datetime.now(),
            deviceID=deviceID,
            config_updated=True,  # Set to True as requested
            **config_data
        )
        
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        
        # Return the latest config in the same format as get_config_data
        configuration = {
            "deviceID": device.deviceID,
            "fileDownloadState": device.fileDownloadState,
            "status": DeviceDataController.build_device_status(db, device, new_config),
            "configs": {}
        }
        
        for i in range(1, 11):
            config_value = getattr(new_config, f'config{i}', None)
            if config_value is not None:
                configuration["configs"][f'config{i}'] = config_value
                
        return configuration
    
    @staticmethod
    def get_config_update_status(db: Session, org_token: str, deviceID: int):
        """Get config update status. Returns data if config_updated=False, just status if True."""
        try:
            from controllers.user_org import OrganisationController
            
            # Validate org_token and get organisation_id
            organisation_id = OrganisationController.get_organisation_id_by_token(db, org_token)
            if not organisation_id:
                raise HTTPException(status_code=404, detail="Invalid organization token!")
            
            # Get device and verify it belongs to the organization
            device = db.query(Devices).filter_by(deviceID=deviceID).first()
            if not device:
                raise HTTPException(status_code=404, detail="Device not found!")
            
            # Get the device's profile and check if it belongs to the organization
            profile = db.query(Profiles).filter_by(id=device.profile).first()
            if not profile or str(profile.organisation_id) != organisation_id:
                raise HTTPException(status_code=403, detail="Device does not belong to your organization!")
            
            # Get the latest config
            latest_config = db.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
            
            if not latest_config:
                # No config exists yet
                # Build status with None config_updated
                status = DeviceDataController.build_device_status(db, device, None)
                status["config_updated"] = None  # Override to show no config exists
                
                return {
                    "deviceID": deviceID,
                    "status": status,
                    "message": "No configuration found for this device"
                }
            
            # Check config_updated status
            if latest_config.config_updated == False:
                # Prepare configuration data to return
                configuration = {
                    "deviceID": device.deviceID,
                    "fileDownloadState": device.fileDownloadState,
                    "status": DeviceDataController.build_device_status(db, device, latest_config),
                    "configs": {}
                }
                # Override config_updated to True since device is now getting the config
                configuration["status"]["config_updated"] = True
                
                for i in range(1, 11):
                    config_value = getattr(latest_config, f'config{i}', None)
                    if config_value is not None:
                        configuration["configs"][f'config{i}'] = config_value
                
                # Update config_updated to True after device retrieves the configuration
                latest_config.config_updated = True
                db.commit()
                        
                return configuration
            else:
                # Return just updated status when config_updated is True
                return {
                    "deviceID": deviceID,
                    "status": DeviceDataController.build_device_status(db, device, latest_config),
                    "message": "Configuration is up to date"
                }
        except Exception as e:
            # Rollback any database changes if there's an error
            db.rollback()
            if isinstance(e, HTTPException):
                raise e
            else:
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
