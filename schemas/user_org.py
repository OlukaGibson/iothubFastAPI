from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid
import datetime

class OrganisationBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True

class OrganisationCreate(OrganisationBase):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class OrganisationUpdate(OrganisationBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class OrganisationRead(OrganisationBase):
    id: uuid.UUID
    token: str
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True

class OrganisationResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    token: str
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True



class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str
    token: Optional[str] = None
    organisation_name: Optional[str] = None  # If not provided, auto-create org

    class Config:
        from_attributes = True

class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserRead(UserBase):
    id: uuid.UUID
    token: str
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    organisations: Optional[List[OrganisationRead]] = None

class OrganisationMembership(BaseModel):
    """User's membership in an organization with role information."""
    org_id: uuid.UUID
    org_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class TokenPair(BaseModel):
    """JWT token pair with basic and organization tokens."""
    basic_token: str
    org_token: str

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Enhanced login response with both token types and organization info."""
    message: str
    user_id: uuid.UUID
    username: str
    email: str
    is_admin: bool
    tokens: TokenPair
    organizations: List[OrganisationMembership]

    class Config:
        from_attributes = True
