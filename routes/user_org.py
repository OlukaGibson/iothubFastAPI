from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from controllers.user_org import UserController, OrganisationController, get_db
from schemas.user_org import UserCreate, UserRead, OrganisationCreate, OrganisationRead, OrganisationUpdate, UserUpdate, LoginResponse
from utils.error_codes import ResponseModel
from utils.security import get_current_user, get_admin_user, get_current_user_or_admin
import uuid
from typing import List
import jwt
from datetime import datetime, timedelta
import os

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_DELTA_SECONDS = int(os.getenv("JWT_EXP_DELTA_SECONDS", "3600"))

# Example: In-memory blacklist (use Redis or DB for production)
jwt_blacklist = set()

def create_jwt_token(user):
    """Create a basic JWT token with user information only."""
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,  # Assuming user model has is_admin attribute
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_org_jwt_token(user):
    """Create an organization-embedded JWT token with user and organization information."""
    # Get user's organizations with roles
    org_info = []
    org_ids = []
    primary_org_id = None
    primary_org_role = None
    
    for assoc in user.user_organisations:
        org_info.append({
            "org_id": str(assoc.organisation.id),
            "org_name": assoc.organisation.name,
            "role": assoc.role.value,
            "is_active": assoc.organisation.is_active
        })
        org_ids.append(str(assoc.organisation.id))
        
        # Set first active organization as primary
        if primary_org_id is None and assoc.organisation.is_active:
            primary_org_id = str(assoc.organisation.id)
            primary_org_role = assoc.role.value
    
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
        "org_ids": org_ids,  # All organizations user belongs to
        "primary_org_id": primary_org_id,  # Primary/default organization
        "primary_org_role": primary_org_role,  # Role in primary organization
        "org_info": org_info,  # Detailed organization information
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@router.post("/login")
def login(
    email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    from models.user_org import User
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create organization token with embedded org context
    org_token = create_org_jwt_token(user)
    
    return {
        "message": "Login successful",
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "token": org_token
    }

@router.post("/logout")
def logout(token: str = Body(..., embed=True)):
    # Add the token to the blacklist
    jwt_blacklist.add(token)
    return {"message": "Logout successful"}

def is_token_blacklisted(token: str) -> bool:
    return token in jwt_blacklist

@router.post("/users", response_model=UserRead)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create a new user. Requires admin privileges."""
    db_user = UserController.create_user(user, db)
    return db_user

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific user. Requires admin privileges or user accessing their own data."""
    # Check if user is admin or accessing their own data
    if not current_user.is_admin and str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only access your own data or must be an admin."
        )
    
    return UserController.get_user(user_id, db)

@router.get("/users", response_model=List[UserRead])
def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get all users. Requires admin privileges."""
    return UserController.get_all_users(db)

# @router.put("/users/{user_id}", response_model=UserRead)
# def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
#     return UserController.update_user(user_id, user_update, db)

@router.post("/organisations", response_model=OrganisationRead)
def create_organisation(
    org: OrganisationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create a new organisation. Requires admin privileges."""
    # org now includes email and password for admin creation
    return OrganisationController.create_organisation(org, db)

@router.get("/organisations/{org_id}", response_model=OrganisationRead)
def get_organisation(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get a specific organisation. Requires admin privileges."""
    return OrganisationController.get_organisation(org_id, db)

@router.get("/organisations", response_model=List[OrganisationRead])
def get_all_organisations(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get all organisations. Requires admin privileges."""
    return OrganisationController.get_all_organisations(db)

# @router.put("/organisations/{org_id}", response_model=OrganisationRead)
# def update_organisation(org_id: uuid.UUID, org_update: OrganisationUpdate, db: Session = Depends(get_db)):
#     return OrganisationController.update_organisation(org_id, org_update, db)

