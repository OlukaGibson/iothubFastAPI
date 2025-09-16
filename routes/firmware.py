from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response, Request
from sqlalchemy.orm import Session
from controllers.firmware import FirmwareController
from schemas.firmware import FirmwareUpload, FirmwareRead, FirmwareUpdate
from utils.security import get_current_user, get_user_with_org_context
from utils.database_config import get_db
from models.firmware import Firmware
import os
import uuid
import re

router = APIRouter()

def get_organisation_id_from_token(user_data):
    """Get organization ID from JWT token organization context."""
    if hasattr(user_data, 'token_primary_org_id'):
        primary_org_id = user_data.token_primary_org_id
    else:
        # Fallback: try to get from dict format (for compatibility)
        primary_org_id = user_data.get('primary_org_id') if hasattr(user_data, 'get') else None
    
    if not primary_org_id:
        raise HTTPException(status_code=403, detail="No primary organization found in token.")
    return uuid.UUID(str(primary_org_id))

def parse_range_header(range_header: str, file_size: int):
    """Parse HTTP Range header and return start and end byte positions."""
    if not range_header:
        return None, None
    
    # Range header format: "bytes=start-end" or "bytes=start-" or "bytes=-suffix"
    range_match = re.match(r'bytes=(\d*)-(\d*)', range_header)
    if not range_match:
        return None, None  # Invalid format, ignore range
    
    start_str, end_str = range_match.groups()
    
    try:
        # Handle different range formats
        if start_str and end_str:
            # bytes=start-end
            start = int(start_str)
            end = int(end_str)
        elif start_str and not end_str:
            # bytes=start-
            start = int(start_str)
            end = file_size - 1
        elif not start_str and end_str:
            # bytes=-suffix (last N bytes)
            suffix = int(end_str)
            start = max(0, file_size - suffix)
            end = file_size - 1
        else:
            return None, None  # Invalid format
        
        # Validate range
        if start < 0 or end >= file_size or start > end:
            # Return special values to indicate range not satisfiable
            return -1, -1
        
        return start, end
    except (ValueError, TypeError):
        return None, None  # Invalid numbers, ignore range

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
    user_data = Depends(get_user_with_org_context)
):
    """Upload firmware. Requires organization token - firmware will be attached to the organization from the JWT token."""
    organisation_id = get_organisation_id_from_token(user_data)
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
    user_data = Depends(get_user_with_org_context)
):
    """List firmwares in the user's organization. Requires organization token."""
    organisation_id = get_organisation_id_from_token(user_data)
    return FirmwareController.list_firmwares(db, organisation_id)

@router.get("/firmware/{firmware_id}", response_model=FirmwareRead)
def get_firmware(
    firmware_id: str,
    db: Session = Depends(get_db),
    user_data = Depends(get_user_with_org_context)
):
    """Get specific firmware. Requires organization token - ensures firmware belongs to user's organization."""
    organisation_id = get_organisation_id_from_token(user_data)
    try:
        firmware_uuid = uuid.UUID(firmware_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid firmware_id format. Must be UUID.")
    
    firmware = db.query(Firmware).filter_by(
        organisation_id=organisation_id,
        id=firmware_uuid
    ).first()
    if not firmware:
        raise HTTPException(status_code=404, detail="Firmware not found for this organisation.")
    return firmware

@router.get("/firmware/{firmware_id}/download/{file_type}")
def download_firmware_file(
    request: Request,
    firmware_id: str,
    file_type: str,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_user_with_org_context)
):
    organisation_id = get_organisation_id_from_token(user_data)
    try:
        firmware_uuid = uuid.UUID(firmware_id)
        organisation_uuid = uuid.UUID(str(organisation_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid firmware_id or organisation_id format. Must be UUID.")
    
    credentials = None  # Set your GCP credentials if needed
    bucket_name = os.getenv("BUCKET_NAME")
    
    # First, get file size to parse range header
    file_data, file_size, blob_path, _, _ = FirmwareController.download_firmware_file_by_id(
        db, organisation_uuid, firmware_uuid, file_type, bucket_name, credentials
    )
    
    # Parse Range header if present
    range_header = request.headers.get("range")
    range_start, range_end = None, None
    
    if range_header:
        range_start, range_end = parse_range_header(range_header, file_size)
        
        # Handle range not satisfiable
        if range_start == -1 and range_end == -1:
            return Response(
                status_code=416,
                headers={
                    "Content-Range": f"bytes */{file_size}",
                    "Accept-Ranges": "bytes"
                }
            )
        
        # If valid range, re-download with range
        if range_start is not None and range_end is not None:
            file_data, file_size, blob_path, range_start, range_end = FirmwareController.download_firmware_file_by_id(
                db, organisation_uuid, firmware_uuid, file_type, bucket_name, credentials, range_start, range_end
            )
    
    # Get firmware version for filename
    firmware = db.query(Firmware).filter_by(
        organisation_id=organisation_uuid,
        id=firmware_uuid
    ).first()
    firmware_version = firmware.firmware_version if firmware else firmware_id
    filename = f"{firmware_version}.{file_type if file_type != 'bootloader' else 'hex'}"
    
    # Prepare response headers
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-cache"
    }
    
    # Set appropriate status code and headers based on range request
    if range_start is not None and range_end is not None:
        # Partial content response (206)
        status_code = 206
        content_length = range_end - range_start + 1
        headers.update({
            "Content-Length": str(content_length),
            "Content-Range": f"bytes {range_start}-{range_end}/{file_size}"
        })
    else:
        # Full content response (200)
        status_code = 200
        headers["Content-Length"] = str(len(file_data))
    
    return Response(
        content=file_data,
        status_code=status_code,
        media_type="application/octet-stream",
        headers=headers
    )

# @router.head("/firmware/{firmware_id}/download/{file_type}")
# def head_firmware_file(
#     firmware_id: str,
#     file_type: str,
#     db: Session = Depends(get_db),
#     user_data: dict = Depends(get_user_with_org_context)
# ):
#     """HEAD endpoint to get file metadata without downloading the content."""
#     organisation_id = get_organisation_id_from_token(user_data)
#     try:
#         firmware_uuid = uuid.UUID(firmware_id)
#         organisation_uuid = uuid.UUID(str(organisation_id))
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid firmware_id or organisation_id format. Must be UUID.")
    
#     credentials = None
#     bucket_name = os.getenv("BUCKET_NAME")
    
#     # Get firmware info without downloading content
#     firmware = FirmwareController.get_firmware_by_id(db, organisation_uuid, firmware_uuid)
#     if file_type == "bin":
#         blob_path = firmware.firmware_string
#     elif file_type == "hex":
#         blob_path = firmware.firmware_string_hex
#     elif file_type == "bootloader":
#         blob_path = firmware.firmware_string_bootloader
#     else:
#         raise HTTPException(status_code=400, detail="Invalid file type requested.")
#     if not blob_path:
#         raise HTTPException(status_code=404, detail="Requested firmware file not found.")
    
#     # Get file size from Google Cloud Storage
#     from google.cloud import storage
#     from google.oauth2 import service_account
#     import json
    
#     if credentials is None:
#         credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
#         if credentials_json:
#             credentials_dict = json.loads(credentials_json)
#             credentials = service_account.Credentials.from_service_account_info(credentials_dict)
#     storage_client = storage.Client(credentials=credentials)
#     bucket = storage_client.bucket(bucket_name or os.getenv("BUCKET_NAME"))
#     blob = bucket.blob(blob_path)
#     blob.reload()
#     file_size = blob.size
    
#     filename = f"{firmware.firmware_version}.{file_type if file_type != 'bootloader' else 'hex'}"
    
#     return Response(
#         status_code=200,
#         headers={
#             "Content-Length": str(file_size),
#             "Accept-Ranges": "bytes",
#             "Content-Type": "application/octet-stream",
#             "Content-Disposition": f"attachment; filename={filename}"
#         }
#     )

@router.get("/firmware/{org_token}/{firmware_id}/download/{file_type}")
def get_firmware_file_with_org(
    request: Request,
    org_token: str,
    firmware_id: str,
    file_type: str,
    db: Session = Depends(get_db)
):
    """GET endpoint to download firmware file with Range header support. Uses org_token to lookup organization from database."""
    
    # Look up organization by token from database
    from controllers.user_org import OrganisationController
    organisation_id = OrganisationController.get_organisation_id_by_token(db, org_token)
    if not organisation_id:
        raise HTTPException(status_code=404, detail="Invalid organization token.")
    
    try:
        firmware_uuid = uuid.UUID(firmware_id)
        organisation_uuid = uuid.UUID(str(organisation_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid firmware_id or organisation_id format. Must be UUID.")
    
    credentials = None  # Set your GCP credentials if needed
    bucket_name = os.getenv("BUCKET_NAME")
    
    # First, get file size to parse range header
    file_data, file_size, blob_path, filename, content_type = FirmwareController.download_firmware_file_by_id(
        db, organisation_uuid, firmware_uuid, file_type, bucket_name, credentials
    )
    
    if not blob_path:
        raise HTTPException(status_code=404, detail="Requested firmware file not found.")
    
    # Parse Range header if present
    range_header = request.headers.get("range")
    range_start, range_end = None, None
    
    if range_header:
        range_start, range_end = parse_range_header(range_header, file_size)
        
        # Handle range not satisfiable
        if range_start == -1 and range_end == -1:
            return Response(
                status_code=416,
                headers={
                    "Content-Range": f"bytes */{file_size}",
                    "Accept-Ranges": "bytes"
                }
            )
        
        # If valid range, re-download with range
        if range_start is not None and range_end is not None:
            file_data, file_size, blob_path, range_start, range_end = FirmwareController.download_firmware_file_by_id(
                db, organisation_uuid, firmware_uuid, file_type, bucket_name, credentials, range_start, range_end
            )
    
    # Get firmware version for filename
    from models.firmware import Firmware
    firmware = db.query(Firmware).filter_by(
        organisation_id=organisation_uuid,
        id=firmware_uuid
    ).first()
    firmware_version = firmware.firmware_version if firmware else firmware_id
    final_filename = f"{firmware_version}.{file_type if file_type != 'bootloader' else 'hex'}"
    
    # Prepare response headers
    headers = {
        "Content-Disposition": f"attachment; filename={final_filename}",
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-cache"
    }
    
    # Set appropriate status code and headers based on range request
    if range_start is not None and range_end is not None:
        # Partial content response (206)
        status_code = 206
        content_length = range_end - range_start + 1
        headers.update({
            "Content-Length": str(content_length),
            "Content-Range": f"bytes {range_start}-{range_end}/{file_size}"
        })
    else:
        # Full content response (200)
        status_code = 200
        headers["Content-Length"] = str(len(file_data))
    
    return Response(
        content=file_data,
        status_code=status_code,
        media_type="application/octet-stream",
        headers=headers
    )

@router.patch("/firmware/{firmware_id}", response_model=FirmwareRead)
def update_firmware_type(
    firmware_id: str,
    firmware_update: FirmwareUpdate,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_user_with_org_context)
):
    organisation_id = get_organisation_id_from_token(user_data)
    try:
        firmware_uuid = uuid.UUID(firmware_id)
        organisation_uuid = uuid.UUID(str(organisation_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid firmware_id or organisation_id format. Must be UUID.")
    
    firmware = FirmwareController.update_firmware_type(
        db, organisation_uuid, firmware_uuid, firmware_update.firmware_type
    )
    return firmware
