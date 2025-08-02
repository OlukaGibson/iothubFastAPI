from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from utils.database_config import Base
from sqlalchemy.sql import func
import uuid
import enum

class FirmwareDownloadState(enum.Enum):
    updated = 'updated'
    pending = 'pending'
    failed = 'failed'

class Devices(Base):
    __tablename__ = 'devices'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=False)
    readkey = Column(String(100), unique=True)
    deviceID = Column(Integer, unique=True)
    writekey = Column(String(100), unique=True)
    networkID = Column(String(100), default=None)
    currentFirmwareVersion = Column(UUID(as_uuid=True), ForeignKey('firmware.id'), default=None)
    previousFirmwareVersion = Column(UUID(as_uuid=True), ForeignKey('firmware.id'), default=None)
    targetFirmwareVersion = Column(UUID(as_uuid=True), ForeignKey('firmware.id'), default=None)
    fileDownloadState = Column(Boolean, default=False)
    profile = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)  # <-- changed to UUID
    firmwareDownloadState = Column(
        Enum('updated', 'pending', 'failed', name='firmware_download_state_enum'),
        default='updated'
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __init__(self, name, readkey, writekey, deviceID, networkID, profile, currentFirmwareVersion, previousFirmwareVersion, targetFirmwareVersion, fileDownloadState, firmwareDownloadState):
        self.name = name
        self.readkey = readkey
        self.writekey = writekey
        self.deviceID = deviceID
        self.networkID = networkID
        self.profile = profile
        self.currentFirmwareVersion = currentFirmwareVersion
        self.previousFirmwareVersion = previousFirmwareVersion
        self.targetFirmwareVersion = targetFirmwareVersion
        self.fileDownloadState = fileDownloadState
        self.firmwareDownloadState = firmwareDownloadState
