from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from utils.database_config import Base
from sqlalchemy.sql import func
import uuid

class DeviceFiles(Base):
    __tablename__ = 'devicefiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviceID = Column(Integer, ForeignKey('devices.deviceID'))
    file = Column(String(100), default=None, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __init__(self, deviceID, file):
        self.deviceID = deviceID
        self.file = file
