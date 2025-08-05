from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
import datetime

class DeviceBase(BaseModel):
    name: str
    networkID: Optional[str] = None
    profile: UUID
    currentFirmwareVersion: Optional[UUID] = None
    previousFirmwareVersion: Optional[UUID] = None
    targetFirmwareVersion: Optional[UUID] = None
    fileDownloadState: Optional[bool] = False
    firmwareDownloadState: Optional[str] = "updated"

    class Config:
        from_attributes = True

class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: UUID
    readkey: str
    writekey: str
    deviceID: int
    created_at: Optional[datetime.datetime]
    firmwareDownloadState: str
    profile_name: Optional[str] = None
    last_posted_time: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class DeviceDetailResponse(BaseModel):
    id: UUID
    created_at: Optional[datetime.datetime]
    name: str
    readkey: str
    writekey: str
    deviceID: int
    profile: UUID
    currentFirmwareVersion: Optional[str] = None
    targetFirmwareVersion: Optional[str] = None
    previousFirmwareVersion: Optional[str] = None
    networkID: Optional[str] = None
    fileDownloadState: Optional[bool] = False
    firmwareDownloadState: str
    device_data: List[Dict[str, Any]] = []
    config_data: List[Dict[str, Any]] = []
    meta_data: List[Dict[str, Any]] = []
    field_names: Dict[str, str] = {}  # Maps field1, field2, etc. to real names
    config_names: Dict[str, str] = {}  # Maps config1, config2, etc. to real names
    metadata_names: Dict[str, str] = {}  # Maps metadata1, metadata2, etc. to real names

    class Config:
        from_attributes = True
