from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models.user_org import User, Organisation, UserOrganisation, UserRole
from schemas.user_org import UserCreate, UserRead, OrganisationCreate, OrganisationRead, OrganisationUpdate, UserUpdate
from utils.database_config import get_db
from utils.error_codes import ErrorCodes, ResponseMessages
import uuid
import secrets

class UserController:
    @staticmethod
    def create_user(user: UserCreate, db: Session) -> User:
        # Check if user exists
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail=ResponseMessages.USER_ALREADY_EXISTS.value)
        # Handle organisation
        if user.organisation_name:
            org = db.query(Organisation).filter(Organisation.name == user.organisation_name).first()
            if not org:
                org = Organisation(
                    name=user.organisation_name,
                    token=secrets.token_urlsafe(16),
                    is_active=True
                )
                db.add(org)
                db.commit()
                db.refresh(org)
        else:
            # Auto-create org with username as org name
            org = Organisation(
                name=f"{user.username}_org",
                token=secrets.token_urlsafe(16),
                is_active=True
            )
            db.add(org)
            db.commit()
            db.refresh(org)
        db_user = User(
            username=user.username,
            email=user.email,
            token=secrets.token_urlsafe(16),
            is_active=True
        )
        db_user.set_password(user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Link user to org
        link = UserOrganisation(
            user_id=db_user.id,
            organisation_id=org.id,
            role=UserRole.user
        )
        db.add(link)
        db.commit()
        return db_user

    @staticmethod
    def get_user(user_id: uuid.UUID, db: Session) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=ResponseMessages.USER_NOT_FOUND.value)
        return user

    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()
    
    @staticmethod
    def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=ResponseMessages.USER_NOT_FOUND.value)
        for key, value in user_update.dict(exclude_unset=True).items():
            if key == "password" and value:
                user.set_password(value)
            elif value is not None:
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

class OrganisationController:
    @staticmethod
    def get_all_organisations(db: Session):
        return db.query(Organisation).all()
    @staticmethod
    def create_organisation(org: OrganisationCreate, db: Session) -> Organisation:
        # Check if organisation exists
        if db.query(Organisation).filter(Organisation.name == org.name).first():
            raise HTTPException(status_code=400, detail=ErrorCodes.ORG_ALREADY_EXISTS.value)

        # Check if user exists and is admin
        db_user = db.query(User).filter(User.email == org.email).first()
        if not db_user or not db_user.verify_password(org.password):
            raise HTTPException(status_code=403, detail="Invalid admin credentials.")

        # Check if user is admin in any organisation
        admin_link = db.query(UserOrganisation).filter(
            UserOrganisation.user_id == db_user.id,
            UserOrganisation.role == UserRole.admin
        ).first()
        if not admin_link:
            raise HTTPException(status_code=403, detail="User is not an admin.")

        # Create organisation
        db_org = Organisation(
            name=org.name,
            description=org.description,
            is_active=org.is_active,
            token=secrets.token_urlsafe(16)
        )
        db.add(db_org)
        db.commit()
        db.refresh(db_org)

        # Link existing admin user to new org as admin
        link = UserOrganisation(
            user_id=db_user.id,
            organisation_id=db_org.id,
            role=UserRole.admin
        )
        db.add(link)
        db.commit()
        return db_org

    @staticmethod
    def get_organisation(org_id: uuid.UUID, db: Session) -> Organisation:
        org = db.query(Organisation).filter(Organisation.id == org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail=ResponseMessages.ORG_NOT_FOUND.value)
        return org

    @staticmethod
    def update_organisation(org_id: uuid.UUID, org_update: OrganisationUpdate, db: Session) -> Organisation:
        org = db.query(Organisation).filter(Organisation.id == org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail=ResponseMessages.ORG_NOT_FOUND.value)
        for key, value in org_update.dict(exclude_unset=True).items():
            if value is not None:
                setattr(org, key, value)
        db.commit()
        db.refresh(org)
        return org

    @staticmethod
    def get_organisation_id_by_token(db: Session, org_token: str) -> str:
        """Get organisation ID by token from database."""
        org = db.query(Organisation).filter(Organisation.token == org_token, Organisation.is_active == True).first()
        if not org:
            return None
        return str(org.id)
