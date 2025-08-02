from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ErrorCodes(str, Enum):
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ORG_ALREADY_EXISTS = "ORG_ALREADY_EXISTS"
    ORG_NOT_FOUND = "ORG_NOT_FOUND"
    INVALID_DATA = "INVALID_DATA"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ResponseMessages(str, Enum):
    USER_CREATED = "User created successfully."
    USER_UPDATED = "User updated successfully."
    USER_FOUND = "User found."
    USER_NOT_FOUND = "User not found."
    USER_ALREADY_EXISTS = "User already exists."
    ORG_CREATED = "Organisation created successfully."
    ORG_UPDATED = "Organisation updated successfully."
    ORG_FOUND = "Organisation found."
    ORG_NOT_FOUND = "Organisation not found."
    INVALID_DATA = "Invalid data provided."
    UNKNOWN_ERROR = "An unknown error occurred."


class ResponseModel(BaseModel):
    success: bool
    message: str
    error_code: Optional[ErrorCodes] = None
    data: Optional[dict] = None
