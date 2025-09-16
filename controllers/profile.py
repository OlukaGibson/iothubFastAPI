from sqlalchemy.orm import Session
from models.profile import Profiles
from models.config_value import ConfigValues
from models.metadata_value import MetadataValues
from models.device import Devices  # <-- changed to relative import
from schemas.profile import ProfileCreate, ProfileRead, ProfileWithDevices, DeviceConfigSummary
from typing import List, Optional
from fastapi import HTTPException
import uuid

class ProfileController:
    @staticmethod
    def create_profile(profile: ProfileCreate, db: Session) -> ProfileRead:
        # Check for duplicate profile name in the same organisation
        existing = db.query(Profiles).filter_by(
            organisation_id=profile.organisation_id,
            name=profile.name
        ).first()
        if existing:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Profile name '{profile.name}' already exists in this organisation.")
        # Unpack fields/configs/metadata from dicts to model columns
        fields = profile.fields or {}
        configs = profile.configs or {}
        metadata = profile.metadata or {}
        new_profile = Profiles(
            organisation_id=profile.organisation_id,
            name=profile.name,
            description=profile.description,
            **fields,
            **configs,
            **metadata,
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        
        # Convert back to proper format for response
        response_fields = {f'field{i}': getattr(new_profile, f'field{i}') for i in range(1, 16) if getattr(new_profile, f'field{i}')}
        response_configs = {f'config{i}': getattr(new_profile, f'config{i}') for i in range(1, 11) if getattr(new_profile, f'config{i}')}
        response_metadata = {}
        for i in range(1, 16):
            val = getattr(new_profile, f'metadata{i}', None)
            if val is not None:
                response_metadata[f'metadata{i}'] = val
        
        return ProfileRead(
            id=new_profile.id,
            organisation_id=new_profile.organisation_id,
            name=new_profile.name,
            description=new_profile.description,
            created_at=new_profile.created_at,
            fields=response_fields,
            configs=response_configs,
            metadata=response_metadata
        )

    @staticmethod
    def get_profiles(db: Session, organisation_id: uuid.UUID) -> List[ProfileWithDevices]:
        profiles = db.query(Profiles).filter_by(organisation_id=organisation_id).all()
        result = []
        for profile in profiles:
            device_count = db.query(Devices).filter_by(profile=profile.id).count()
            fields = {f'field{i}': getattr(profile, f'field{i}') for i in range(1, 16) if getattr(profile, f'field{i}')}
            configs = {f'config{i}': getattr(profile, f'config{i}') for i in range(1, 11) if getattr(profile, f'config{i}')}
            # Ensure metadata is always a dict
            metadata = {}
            for i in range(1, 16):
                val = getattr(profile, f'metadata{i}', None)
                if val is not None:
                    metadata[f'metadata{i}'] = val
            result.append(ProfileWithDevices(
                id=profile.id,
                organisation_id=profile.organisation_id,
                name=profile.name,
                description=profile.description,
                created_at=profile.created_at,
                fields=fields,
                configs=configs,
                metadata=metadata,
                device_count=device_count,
                devices=[]
            ))
        return result

    @staticmethod
    def get_profile(profile_id: uuid.UUID, db: Session, organisation_id: uuid.UUID) -> ProfileWithDevices:
        profile = db.query(Profiles).filter_by(id=profile_id, organisation_id=organisation_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        devices = db.query(Devices).filter_by(profile=profile_id).all()
        device_list = []
        for device in devices:
            recent_config = db.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by(ConfigValues.created_at.desc()).first()
            config_values = {}
            if recent_config:
                config_values['config_updated'] = recent_config.config_updated
                for i in range(1, 11):
                    val = getattr(recent_config, f'config{i}', None)
                    if val:
                        config_values[f'config{i}'] = val
            device_list.append(DeviceConfigSummary(
                name=device.name,
                deviceID=str(device.deviceID),
                recent_config=config_values
            ))
        fields = {f'field{i}': getattr(profile, f'field{i}') for i in range(1, 16) if getattr(profile, f'field{i}')}
        configs = {f'config{i}': getattr(profile, f'config{i}') for i in range(1, 11) if getattr(profile, f'config{i}')}
        # Ensure metadata is always a dict
        metadata = {}
        for i in range(1, 16):
            val = getattr(profile, f'metadata{i}', None)
            if val is not None:
                metadata[f'metadata{i}'] = val
        return ProfileWithDevices(
            id=profile.id,
            organisation_id=profile.organisation_id,
            name=profile.name,
            description=profile.description,
            created_at=profile.created_at,
            fields=fields,
            configs=configs,
            metadata=metadata,
            device_count=len(devices),
            devices=device_list
        )
