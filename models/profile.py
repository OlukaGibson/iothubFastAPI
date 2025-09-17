from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from utils.database_config import Base
from sqlalchemy.sql import func
import uuid

class Profiles(Base):
    __tablename__ = 'profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), nullable=False)
    name = Column(String(100), unique=True) # Change this later as iy's unique per organisation
    description = Column(String(100), default=None)
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
    created_at = Column(DateTime, server_default=func.now())

    def __init__(
        self,
        organisation_id,
        name,
        description,
        field1=None, field2=None, field3=None, field4=None, field5=None,
        field6=None, field7=None, field8=None, field9=None, field10=None,
        field11=None, field12=None, field13=None, field14=None, field15=None,
        config1=None, config2=None, config3=None, config4=None, config5=None,
        config6=None, config7=None, config8=None, config9=None, config10=None,
        metadata1=None, metadata2=None, metadata3=None, metadata4=None, metadata5=None,
        metadata6=None, metadata7=None, metadata8=None, metadata9=None, metadata10=None,
        metadata11=None, metadata12=None, metadata13=None, metadata14=None, metadata15=None
    ):
        self.organisation_id = organisation_id
        self.name = name
        self.description = description
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
