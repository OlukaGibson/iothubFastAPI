from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from utils.database_config import Base
import uuid

class ConfigValues(Base):
    __tablename__ = 'configvalues'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviceID = Column(Integer, ForeignKey('devices.deviceID'))
    created_at = Column(DateTime)
    config1 = Column(String(100), default=None)
    config2 = Column(String(100), default=None)
    config3 = Column(String(100), default=None)
    config4 = Column(String(100), default=None)
    config5 = Column(String(100), default=None)
    config6 = Column(String(100), default=None)
    config7 = Column(String(100), default=None)
    config8 = Column(String(100), default=None)
    config9 = Column(String(100), default=None)
    config10 = Column(String(100), default=None)
    # add a boolean field to indicate if the config is updated
    config_updated = Column(Boolean, default=False)

    def __init__(self, created_at, deviceID, config1, config2, config3, config4, config5, config6, config7, config8, config9, config10, config_updated=False):
        self.created_at = created_at
        self.deviceID = deviceID
        self.config1 = config1
        self.config2 = config2
        self.config3 = config3
        self.config4 = config4
        self.config5 = config5
        self.config6 = config6
        self.config7 = config7
        self.config8 = config8
        self.config9 = config9
        self.config10 = config10
        self.config_updated = config_updated
