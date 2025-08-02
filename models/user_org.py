from sqlalchemy import Column, Boolean, String, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from utils.base import Base  # <-- changed import
import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID
from utils.security import get_password_hash
from utils.security import verify_password

# Define roles as an Enum
class UserRole(enum.Enum):
    admin = "admin"
    manager = "manager"
    user = "user"


class UserOrganisation(Base):
    """Association table for users, organisations, and roles."""
    __tablename__ = "user_organisations"
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey('organisations.id'), primary_key=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="user_organisations")
    organisation = relationship("Organisation", back_populates="user_organisations")


class Organisation(Base):
    """Organisation model representing a company or group."""
    __tablename__ = "organisations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_organisations = relationship("UserOrganisation", back_populates="organisation", cascade="all, delete-orphan", overlaps="users")
    users = relationship("User", secondary="user_organisations", back_populates="organisations", overlaps="organisation,user_organisations,user")

    def __repr__(self):
        return f"<Organisation(id={self.id}, name={self.name})>"


class User(Base):
    """User model representing an application user."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_organisations = relationship("UserOrganisation", back_populates="user", cascade="all, delete-orphan", overlaps="users")
    organisations = relationship("Organisation", secondary="user_organisations", back_populates="users", overlaps="organisation,user_organisations,user")

    def set_password(self, password: str):
        """Hashes and sets the user's password."""
        self.hashed_password = get_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Verifies a password against the stored hash."""
        return verify_password(password, self.hashed_password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

# Suggestions for further improvements:
# - Add unique constraints/indexes at the database level for username, email, and token.
# - Add validation for email format and password strength.
# - Consider using SQLAlchemy events for auditing changes.
# - Add methods for soft deletion if needed (e.g., is_deleted flag).

