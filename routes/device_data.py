from fastapi import APIRouter, Depends, HTTPException, Request, Body, Query
from sqlalchemy.orm import Session
from controllers.device_data import DeviceDataController, MetadataValuesController, ConfigValuesController
from schemas.device_data import DeviceDataCreate, MetadataValuesCreate, ConfigValuesCreate
from utils.database_config import get_db

router = APIRouter()

@router.post("/device_data/update")
def update_device_data(
    writekey: str = Body(..., embed=True),
    fields: dict = Body(...),
    db: Session = Depends(get_db)
):
    return DeviceDataController.update_device_data(db, writekey, fields)

@router.post("/device_data/bulk_update/{deviceID}")
def bulk_update_device_data(
    deviceID: int,
    updates: list = Body(...),
    db: Session = Depends(get_db)
):
    return DeviceDataController.bulk_update(db, deviceID, updates)

@router.post("/metadata/update")
def update_metadata(
    writekey: str = Body(..., embed=True),
    metadatas: dict = Body(...),
    db: Session = Depends(get_db)
):
    return MetadataValuesController.update_metadata(db, writekey, metadatas)

@router.post("/config/update")
def update_config_data(
    deviceID: int = Body(..., embed=True),
    configs: dict = Body(...),
    db: Session = Depends(get_db)
):
    return ConfigValuesController.update_config_data(db, deviceID, configs)

@router.post("/config/mass_edit")
def mass_edit_config_data(
    device_ids: list = Body(..., embed=True),
    config_values: dict = Body(...),
    db: Session = Depends(get_db)
):
    return ConfigValuesController.mass_edit_config_data(db, device_ids, config_values)

@router.get("/config/{deviceID}")
def get_config_data(
    deviceID: int,
    db: Session = Depends(get_db)
):
    return ConfigValuesController.get_config_data(db, deviceID)

@router.get("/config_update")
def get_config_update(
    org_token: str = Query(..., description="Organization token"),
    deviceID: int = Query(..., description="Device ID"),
    db: Session = Depends(get_db)
):
    """Get device config update status. Returns data if config_updated=False, just updated status if True."""
    return ConfigValuesController.get_config_update_status(db, org_token, deviceID)
