from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import uuid
import secrets
from utils.base import Base  # <-- changed import

# Load environment variables from .env file
load_dotenv()

# Set your database URL here (default to SQLite if not set)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./iot_database.db")

# Configure engine with connection pooling and timeout handling
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "connect_timeout": 10,
            "application_name": "iothub_fastapi"
        }
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_all_tables():
    """
    Dynamically import all model modules and create tables for all models inheriting from Base.
    This ensures that any changes in models are reflected in the database at app startup.
    """
    import importlib
    import pkgutil
    import sys
    from pathlib import Path

    models_path = Path(__file__).parent.parent / "models"
    sys.path.append(str(models_path.parent))

    # Dynamically import all modules in the models package
    for _, module_name, _ in pkgutil.iter_modules([str(models_path)]):
        importlib.import_module(f"models.{module_name}")

    # Move model imports here to avoid circular import
    from models.user_org import User, Organisation, UserOrganisation, UserRole

    # Now create all tables
    Base.metadata.create_all(bind=engine)


    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_org_name = os.getenv('ADMIN_ORGANISATION')

    if not all([admin_email, admin_password, admin_username, admin_org_name]):
        print("[WARNING] Admin credentials or organisation not set in .env. Skipping admin/organisation creation.")
        return

    db = SessionLocal()
    try:
        # Check if organisation exists
        org = db.query(Organisation).filter(Organisation.name == admin_org_name).first()
        if not org:
            org = Organisation(
                name=admin_org_name,
                description=f"Default organisation {admin_org_name}",
                is_active=True,
                token=secrets.token_urlsafe(16)
            )
            db.add(org)
            db.commit()
            db.refresh(org)

        # Check if admin user exists
        user = db.query(User).filter(User.email == admin_email).first()
        if not user:
            user = User(
                username=admin_username,
                email=admin_email,
                token=secrets.token_urlsafe(16),
                is_active=True
            )
            user.set_password(admin_password)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Check if user-organisation admin link exists
        link = db.query(UserOrganisation).filter(
            UserOrganisation.user_id == user.id,
            UserOrganisation.organisation_id == org.id
        ).first()
        if not link:
            link = UserOrganisation(
                user_id=user.id,
                organisation_id=org.id,
                role=UserRole.admin
            )
            db.add(link)
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
