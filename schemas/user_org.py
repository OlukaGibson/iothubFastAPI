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
