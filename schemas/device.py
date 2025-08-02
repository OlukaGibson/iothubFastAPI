from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
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
    firmwareDownloadState: Optional[str]
    profile_name: Optional[str] = None
    last_posted_time: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True
