from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from controllers.user_org import UserController, OrganisationController, get_db
from schemas.user_org import UserCreate, UserRead, OrganisationCreate, OrganisationRead, OrganisationUpdate, UserUpdate
from utils.error_codes import ResponseModel
import uuid
from typing import List

router = APIRouter()

@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserController.create_user(user, db)
    return db_user

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return UserController.get_user(user_id, db)

@router.get("/users", response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    return UserController.get_all_users(db)

# @router.put("/users/{user_id}", response_model=UserRead)
# def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
#     return UserController.update_user(user_id, user_update, db)

@router.post("/organisations", response_model=OrganisationRead)
def create_organisation(org: OrganisationCreate, db: Session = Depends(get_db)):
    # org now includes email and password for admin creation
    return OrganisationController.create_organisation(org, db)

@router.get("/organisations/{org_id}", response_model=OrganisationRead)
def get_organisation(org_id: uuid.UUID, db: Session = Depends(get_db)):
    return OrganisationController.get_organisation(org_id, db)

@router.get("/organisations", response_model=List[OrganisationRead])
def get_all_organisations(db: Session = Depends(get_db)):
    return OrganisationController.get_all_organisations(db)

# @router.put("/organisations/{org_id}", response_model=OrganisationRead)
# def update_organisation(org_id: uuid.UUID, org_update: OrganisationUpdate, db: Session = Depends(get_db)):
#     return OrganisationController.update_organisation(org_id, org_update, db)

