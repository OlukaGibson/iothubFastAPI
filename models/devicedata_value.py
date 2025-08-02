from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from utils.database_config import Base
import uuid

class DeviceData(Base):
    __tablename__ = 'devicedata'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entryID = Column(Integer)
    deviceID = Column(Integer, ForeignKey('devices.deviceID'))
    created_at = Column(DateTime)
    field1 = Column(String(100), default=None)
    field2 = Column(String(100), default=None)
    field3 = Column(String(100), default=None)
    field4 = Column(String(100), default=None)
    field5 = Column(String(100), default=None)
    field6 = Column(String(100), default=None)
    field7 = Column(String(100), default=None)
    field8 = Column(String(100), default=None)
    field9 = Column(String(100), default=None)
    field10 = Column(String(100), default=None)
    field11 = Column(String(100), default=None)
    field12 = Column(String(100), default=None)
    field13 = Column(String(100), default=None)
    field14 = Column(String(100), default=None)
    field15 = Column(String(100), default=None)

    __table_args__ = (UniqueConstraint('deviceID', 'entryID', name='unique_device_entry'),)

    @classmethod
    def get_next_entry_id(cls, db_session, device_id):
        """Get the next available entry ID for a specific device."""
        max_entry = db_session.query(func.max(cls.entryID)).filter(cls.deviceID == device_id).scalar()
        return 1 if max_entry is None else max_entry + 1

    def __init__(self, created_at, deviceID, entryID, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15):
        self.created_at = created_at
        self.deviceID = deviceID
        self.entryID = entryID
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        self.field4 = field4
        self.field5 = field5
        self.field6 = field6
        self.field7 = field7
        self.field8 = field8
        self.field9 = field9
        self.field10 = field10
        self.field11 = field11
        self.field12 = field12
        self.field13 = field13
        self.field14 = field14
        self.field15 = field15
