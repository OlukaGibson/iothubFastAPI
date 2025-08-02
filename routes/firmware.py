from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from sqlalchemy.orm import Session
from controllers.firmware import FirmwareController
from schemas.firmware import FirmwareUpload, FirmwareRead
from utils.security import get_current_user
from utils.database_config import get_db
from models.firmware import Firmware
import os
import uuid

router = APIRouter()

def get_organisation_id_from_user(user=Depends(get_current_user)):
    # Assumes user.organisations[0].id is the current org; adjust as needed
    if not user.organisations:
        raise HTTPException(status_code=403, detail="User not associated with any organisation.")
    return user.organisations[0].id

@router.post("/firmware/upload", response_model=FirmwareRead)
async def upload_firmware(
    firmware_version: str = Form(...),
    firmware_type: str = Form("beta"),
    description: str = Form(None),
    change1: str = Form(None),
    change2: str = Form(None),
    change3: str = Form(None),
    change4: str = Form(None),
    change5: str = Form(None),
    change6: str = Form(None),
    change7: str = Form(None),
    change8: str = Form(None),
    change9: str = Form(None),
    change10: str = Form(None),
    firmware_file: UploadFile = File(...),
    firmware_bootloader: UploadFile = File(None),
    db: Session = Depends(get_db),
    organisation_id: str = Depends(get_organisation_id_from_user)
):
    firmware_data = {
        "firmware_version": firmware_version,
        "firmware_type": firmware_type,
        "description": description,
        "change1": change1,
        "change2": change2,
        "change3": change3,
        "change4": change4,
        "change5": change5,
        "change6": change6,
        "change7": change7,
        "change8": change8,
        "change9": change9,
        "change10": change10,
    }
    credentials = None  # Set your GCP credentials if needed
    bucket_name = os.getenv("BUCKET_NAME")
    firmware = FirmwareController.upload_firmware(
        db, organisation_id, firmware_data, firmware_file, firmware_bootloader, bucket_name, credentials
    )
    return firmware

@router.get("/firmware", response_model=list[FirmwareRead])
def list_firmwares(
    db: Session = Depends(get_db),
    organisation_id: str = Depends(get_organisation_id_from_user)
):
    return FirmwareController.list_firmwares(db, organisation_id)

@router.get("/firmware/{firmware_id}", response_model=FirmwareRead)
def get_firmware(
    firmware_id: str,
    db: Session = Depends(get_db),
    organisation_id: str = Depends(get_organisation_id_from_user)
):
    try:
        firmware_uuid = uuid.UUID(firmware_id)
        organisation_uuid = uuid.UUID(str(organisation_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid firmware_id or organisation_id format. Must be UUID.")
    firmware = db.query(Firmware).filter_by(
        organisation_id=organisation_uuid,
        id=firmware_uuid
    ).first()
    if not firmware:
        raise HTTPException(status_code=404, detail="Firmware not found for this organisation.")
    return firmware

@router.get("/firmware/{firmware_id}/download/{file_type}")
def download_firmware_file(
    firmware_id: str,
    file_type: str,
    db: Session = Depends(get_db),
    organisation_id: str = Depends(get_organisation_id_from_user)
):
    try:
        firmware_uuid = uuid.UUID(firmware_id)
        organisation_uuid = uuid.UUID(str(organisation_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid firmware_id or organisation_id format. Must be UUID.")
    credentials = None  # Set your GCP credentials if needed
    bucket_name = os.getenv("BUCKET_NAME")
    file_data, file_size, blob_path = FirmwareController.download_firmware_file_by_id(
        db, organisation_uuid, firmware_uuid, file_type, bucket_name, credentials
    )
    # Get firmware version for filename
    firmware = db.query(Firmware).filter_by(
        organisation_id=organisation_uuid,
        id=firmware_uuid
    ).first()
    firmware_version = firmware.firmware_version if firmware else firmware_id
    filename = f"{firmware_version}.{file_type if file_type != 'bootloader' else 'hex'}"
    return Response(
        content=file_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes"
        }
    )
