from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from utils.database_config import Base
import uuid

class MetadataValues(Base):
    __tablename__ = 'metadatavalues'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviceID = Column(Integer, ForeignKey('devices.deviceID'))
    created_at = Column(DateTime)
    metadata1 = Column(String(100), default=None)
    metadata2 = Column(String(100), default=None)
    metadata3 = Column(String(100), default=None)
    metadata4 = Column(String(100), default=None)
    metadata5 = Column(String(100), default=None)
    metadata6 = Column(String(100), default=None)
    metadata7 = Column(String(100), default=None)
    metadata8 = Column(String(100), default=None)
    metadata9 = Column(String(100), default=None)
    metadata10 = Column(String(100), default=None)
    metadata11 = Column(String(100), default=None)
    metadata12 = Column(String(100), default=None)
    metadata13 = Column(String(100), default=None)
    metadata14 = Column(String(100), default=None)
    metadata15 = Column(String(100), default=None)

    def __init__(self, created_at, deviceID, metadata1, metadata2, metadata3, metadata4, metadata5, metadata6, metadata7, metadata8, metadata9, metadata10, metadata11, metadata12, metadata13, metadata14, metadata15):
        self.created_at = created_at
        self.deviceID = deviceID
        self.metadata1 = metadata1
        self.metadata2 = metadata2
        self.metadata3 = metadata3
        self.metadata4 = metadata4
        self.metadata5 = metadata5
        self.metadata6 = metadata6
        self.metadata7 = metadata7
        self.metadata8 = metadata8
        self.metadata9 = metadata9
        self.metadata10 = metadata10
        self.metadata11 = metadata11
        self.metadata12 = metadata12
        self.metadata13 = metadata13
        self.metadata14 = metadata14
        self.metadata15 = metadata15
