from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from controllers.profile import ProfileController
from schemas.profile import ProfileCreate, ProfileRead, ProfileWithDevices
from utils.database_config import get_db
from utils.security import get_current_user
import uuid
from typing import List

router = APIRouter()

def get_organisation_id_from_user(user=Depends(get_current_user)):
    # Assumes user.organisations[0].id is the current org; adjust as needed
    if not user.organisations:
        raise HTTPException(status_code=403, detail="User not associated with any organisation.")
    return user.organisations[0].id

@router.post("/profiles", response_model=ProfileRead)
def create_profile(
    profile: ProfileCreate,
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    # Override organisation_id from user
    profile_data = profile.copy(update={"organisation_id": organisation_id})
    return ProfileController.create_profile(profile_data, db)

@router.get("/profiles", response_model=List[ProfileWithDevices])
def get_profiles(
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    return ProfileController.get_profiles(db, organisation_id)

@router.get("/profiles/{profile_id}", response_model=ProfileWithDevices)
def get_profile(
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
    organisation_id: uuid.UUID = Depends(get_organisation_id_from_user)
):
    return ProfileController.get_profile(profile_id, db, organisation_id)
