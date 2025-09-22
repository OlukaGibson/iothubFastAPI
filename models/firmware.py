from sqlalchemy import Column, Boolean, String, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from utils.database_config import Base as base
import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID

class FirmwareType(enum.Enum):
    stable = "stable"
    beta = "beta"
    deprecated = "deprecated"
    legacy = "legacy"

class Firmware(base):
    """Firmware model representing firmware versions."""
    __tablename__ = "firmware"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    firmware_version = Column(String(100), nullable=False)
    firmware_string = Column(String(100), nullable=False)
    firmware_string_hex = Column(String(100), default=None, nullable=True)
    firmware_string_bootloader = Column(String(100), default=None, nullable=True)
    firmware_type = Column(Enum(FirmwareType), nullable=True, default=FirmwareType.beta)
    description = Column(String(255), default=None, nullable=True)
    # firmware CRC32 checksum
    crc32 = Column(String(100), default=None, nullable=True)
    change1 = Column(String(255), default=None)
    change2 = Column(String(255), default=None)
    change3 = Column(String(255), default=None)
    change4 = Column(String(255), default=None)
    change5 = Column(String(255), default=None)
    change6 = Column(String(255), default=None)
    change7 = Column(String(255), default=None)
    change8 = Column(String(255), default=None)
    change9 = Column(String(255), default=None)
    change10 = Column(String(255), default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Optional: relationship to Organisation
    # organisation = relationship("Organisation", back_populates="firmwares")

    def __repr__(self):
        return f"<Firmware(id={self.id}, version={self.firmware_version})>"
