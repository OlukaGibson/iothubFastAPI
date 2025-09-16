from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
import datetime

class DeviceDataBase(BaseModel):
    deviceID: int
    fields: Optional[Dict[str, Optional[str]]] = None

class DeviceDataCreate(DeviceDataBase):
    created_at: Optional[datetime.datetime] = None

class DeviceDataRead(DeviceDataBase):
    id: UUID
    entryID: int
    created_at: datetime.datetime
    fields: Dict[str, Optional[str]]

class MetadataValuesBase(BaseModel):
    deviceID: int
    metadatas: Optional[Dict[str, Optional[str]]] = None

class MetadataValuesCreate(MetadataValuesBase):
    created_at: Optional[datetime.datetime] = None

class MetadataValuesRead(MetadataValuesBase):
    id: UUID
    created_at: datetime.datetime
    metadatas: Dict[str, Optional[str]]

class ConfigValuesBase(BaseModel):
    deviceID: int
    config_updated: bool = False
    configs: Optional[Dict[str, Optional[str]]] = None

class ConfigValuesCreate(ConfigValuesBase):
    created_at: Optional[datetime.datetime] = None

class ConfigValuesRead(ConfigValuesBase):
    id: UUID
    created_at: datetime.datetime
    configs: Dict[str, Optional[str]]
