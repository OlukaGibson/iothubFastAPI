from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
import enum

class FirmwareType(str, enum.Enum):
    stable = "stable"
    beta = "beta"
    deprecated = "deprecated"
    legacy = "legacy"

class FirmwareBase(BaseModel):
    organisation_id: UUID
    firmware_version: str
    firmware_type: Optional[FirmwareType] = FirmwareType.beta
    description: Optional[str] = None
    change1: Optional[str] = None
    change2: Optional[str] = None
    change3: Optional[str] = None
    change4: Optional[str] = None
    change5: Optional[str] = None
    change6: Optional[str] = None
    change7: Optional[str] = None
    change8: Optional[str] = None
    change9: Optional[str] = None
    change10: Optional[str] = None

class FirmwareUpload(FirmwareBase):
    pass  # For file uploads, use form/multipart in FastAPI endpoint

class FirmwareResponse(FirmwareBase):
    id: UUID
    firmware_string: str
    firmware_string_hex: Optional[str] = None
    firmware_string_bootloader: Optional[str] = None

    class Config:
        from_attributes = True

class FirmwareRead(FirmwareResponse):
    pass

class FirmwareDownloadRequest(BaseModel):
    organisation_id: UUID
    firmware_version: str
    file_type: str  # "bin", "hex", or "bootloader"

