from pydantic import BaseModel
from typing import Optional

class FirmwareDownload(BaseModel):
    """Enhanced firmware download state with additional metadata"""
    firmwareDownloadState: str  # e.g., "pending", "downloading", "completed", "failed"
    version: str  # e.g., "lcdv42.751"
    fwcrc: str  # e.g., "0x1A2B3C4D"
    firmware_bin_size: Optional[int] = 0  # e.g., 524288 (firmware binary size in bytes)
    
    class Config:
        from_attributes = True

class DeviceStatus(BaseModel):
    """Standardized status structure for all endpoints returning device status"""
    config_updated: bool
    fileDownloadState: bool
    firmwareDownload: FirmwareDownload
    
    class Config:
        from_attributes = True