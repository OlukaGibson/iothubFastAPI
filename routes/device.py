from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from controllers.device import DeviceController
from schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceDetailResponse
from utils.security import get_user_with_org_context
from utils.database_config import get_db
import uuid
from typing import Optional

router = APIRouter()

def safe_uuid_convert(value) -> Optional[uuid.UUID]:
    """Convert string to UUID, return None if invalid"""
    if value is None or value == "":
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return None

def sanitize_device_response(device_data):
    """Sanitize device data to ensure valid UUIDs"""
    if hasattr(device_data, '__dict__'):
        # Handle SQLAlchemy model objects
        data = device_data.__dict__.copy()
    else:
        # Handle dict objects
        data = device_data.copy() if isinstance(device_data, dict) else device_data
    
    # Convert invalid UUID fields to None
    uuid_fields = ['currentFirmwareVersion', 'previousFirmwareVersion', 'targetFirmwareVersion']
    for field in uuid_fields:
        if hasattr(data, field) if not isinstance(data, dict) else field in data:
            value = getattr(data, field) if not isinstance(data, dict) else data[field]
            safe_value = safe_uuid_convert(value)
            if not isinstance(data, dict):
                setattr(data, field, safe_value)
            else:
                data[field] = safe_value
    
    return data

def get_organisation_id_from_token(user_data) -> uuid.UUID:
    """Extract organisation ID from JWT token data stored in User object"""
    # Check if user_data is a User object with JWT token attributes
    if hasattr(user_data, 'token_primary_org_id'):
        primary_org_id = user_data.token_primary_org_id
    else:
        # Fallback: try to get from dict format (for compatibility)
        primary_org_id = user_data.get('primary_org_id') if hasattr(user_data, 'get') else None
    
    if not primary_org_id:
        raise HTTPException(status_code=403, detail="No organization context in token.")
    try:
        return uuid.UUID(str(primary_org_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=403, detail="Invalid organization ID in token.")

@router.post("/device", response_model=DeviceResponse)
def add_device(
    device: DeviceCreate = Body(...),
    db: Session = Depends(get_db),
    user_data = Depends(get_user_with_org_context)
):
    organisation_id = get_organisation_id_from_token(user_data)
    result = DeviceController.create_device(db, organisation_id, device)
    return sanitize_device_response(result)

@router.get("/device", response_model=list[DeviceResponse])
def get_devices(
    db: Session = Depends(get_db),
    user_data = Depends(get_user_with_org_context)
):
    organisation_id = get_organisation_id_from_token(user_data)
    devices = DeviceController.get_devices(db, organisation_id)
    return [sanitize_device_response(device) for device in devices]

@router.get("/device/{deviceID}", response_model=DeviceDetailResponse)
def get_device(
    deviceID: int,
    db: Session = Depends(get_db),
    user_data = Depends(get_user_with_org_context)
):
    organisation_id = get_organisation_id_from_token(user_data)
    result = DeviceController.get_device(db, organisation_id, deviceID)
    if isinstance(result, tuple):  # Error case
        raise HTTPException(status_code=result[1], detail=result[0]['message'])
    return result

# @router.put("/device/{deviceID}", response_model=DeviceResponse)
# def edit_device(
#     deviceID: int,
#     device_update: DeviceUpdate = Body(...),
#     db: Session = Depends(get_db),
#     organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
# ):
#     result = DeviceController.update_device(db, organisation_id, deviceID, device_update)
#     return sanitize_device_response(result)

# @router.post("/device/{deviceID}/update_firmware", response_model=DeviceResponse)
# def update_firmware(
#     deviceID: int,
#     payload: dict = Body(...),
#     db: Session = Depends(get_db),
#     organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
# ):
#     firmwareID = payload.get('firmwareID')
#     firmwareVersion = payload.get('firmwareVersion')
#     if not firmwareID or not firmwareVersion:
#         raise HTTPException(status_code=400, detail="Firmware ID and version required")
#     result = DeviceController.update_firmware(db, organisation_id, deviceID, uuid.UUID(firmwareID), firmwareVersion)
#     return sanitize_device_response(result)

@router.get("/network/selfconfig")
def self_config(
    org_token: str = Query(..., description="Organization token"),
    networkID: str = Query(..., description="Network ID"),
    db: Session = Depends(get_db)
):
    # Look up organization by token from database
    from controllers.user_org import OrganisationController
    organisation_id = OrganisationController.get_organisation_id_by_token(db, org_token)
    if not organisation_id:
        raise HTTPException(status_code=404, detail="Invalid organization token.")
    
    return DeviceController.self_config(db, organisation_id, networkID)
