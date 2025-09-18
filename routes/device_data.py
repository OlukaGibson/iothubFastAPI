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

@router.get("/metadata_update")
def update_metadata_with_status(
    org_token: str = Query(..., description="Organization token"),
    deviceID: int = Query(..., description="Device ID"),
    meta1: str = Query(None, description="Metadata field 1"),
    meta2: str = Query(None, description="Metadata field 2"),
    meta3: str = Query(None, description="Metadata field 3"),
    meta4: str = Query(None, description="Metadata field 4"),
    meta5: str = Query(None, description="Metadata field 5"),
    meta6: str = Query(None, description="Metadata field 6"),
    meta7: str = Query(None, description="Metadata field 7"),
    meta8: str = Query(None, description="Metadata field 8"),
    meta9: str = Query(None, description="Metadata field 9"),
    meta10: str = Query(None, description="Metadata field 10"),
    meta11: str = Query(None, description="Metadata field 11"),
    meta12: str = Query(None, description="Metadata field 12"),
    meta13: str = Query(None, description="Metadata field 13"),
    meta14: str = Query(None, description="Metadata field 14"),
    meta15: str = Query(None, description="Metadata field 15"),
    db: Session = Depends(get_db)
):
    """Update device metadata and return success/failure message with status information."""
    metadata_dict = {
        'metadata1': meta1, 'metadata2': meta2, 'metadata3': meta3, 'metadata4': meta4, 'metadata5': meta5,
        'metadata6': meta6, 'metadata7': meta7, 'metadata8': meta8, 'metadata9': meta9, 'metadata10': meta10,
        'metadata11': meta11, 'metadata12': meta12, 'metadata13': meta13, 'metadata14': meta14, 'metadata15': meta15
    }
    return MetadataValuesController.update_metadata_with_status(db, org_token, deviceID, metadata_dict)

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
