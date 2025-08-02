from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
import datetime

class ProfileBase(BaseModel):
    name: str
    description: Optional[str] = None
    fields: Optional[Dict[str, Optional[str]]] = None
    configs: Optional[Dict[str, Optional[str]]] = None
    metadata: Optional[Dict[str, Optional[str]]] = None

class ProfileCreate(ProfileBase):
    organisation_id: UUID

class ProfileRead(ProfileBase):
    id: UUID
    organisation_id: UUID
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True

class DeviceConfigSummary(BaseModel):
    name: str
    deviceID: str
    recent_config: Dict[str, Optional[str]]

class ProfileWithDevices(ProfileRead):
    device_count: int
    devices: List[DeviceConfigSummary] = []
