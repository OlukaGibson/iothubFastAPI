from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from controllers.device import DeviceController
from schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from utils.security import get_current_user
from utils.database_config import get_db
import uuid

router = APIRouter()

def get_organisation_id_from_user(user=Depends(get_current_user)):
    if not user.organisations:
        raise HTTPException(status_code=403, detail="User not associated with any organisation.")
    return user.organisations[0].id

@router.post("/device", response_model=DeviceResponse)
def add_device(
    device: DeviceCreate = Body(...),
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    return DeviceController.create_device(db, organisation_id, device)

@router.get("/device", response_model=list[DeviceResponse])
def get_devices(
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    return DeviceController.get_devices(db, organisation_id)

@router.get("/device/{deviceID}", response_model=DeviceResponse)
def get_device(
    deviceID: int,
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    return DeviceController.get_device(db, organisation_id, deviceID)

@router.put("/device/{deviceID}", response_model=DeviceResponse)
def edit_device(
    deviceID: int,
    device_update: DeviceUpdate = Body(...),
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    return DeviceController.update_device(db, organisation_id, deviceID, device_update)

@router.post("/device/{deviceID}/update_firmware", response_model=DeviceResponse)
def update_firmware(
    deviceID: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    firmwareID = payload.get('firmwareID')
    firmwareVersion = payload.get('firmwareVersion')
    if not firmwareID or not firmwareVersion:
        raise HTTPException(status_code=400, detail="Firmware ID and version required")
    return DeviceController.update_firmware(db, organisation_id, deviceID, uuid.UUID(firmwareID), firmwareVersion)

@router.get("/device/network/{networkID}/selfconfig")
def self_config(
    networkID: str,
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    return DeviceController.self_config(db, organisation_id, networkID)
