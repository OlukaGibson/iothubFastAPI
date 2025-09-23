from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from models.firmware import Firmware, FirmwareType
from google.cloud import storage
from schemas.firmware import FirmwareUpload
from utils.gcp_utils import load_gcp_credentials
import os, io, uuid, zlib
from intelhex import IntelHex
from google.oauth2 import service_account
import json

class FirmwareController:
    @staticmethod
    def upload_firmware(
        db: Session,
        organisation_id: uuid.UUID,
        firmware_data: dict,
        firmware_file: UploadFile,
        firmware_bootloader: UploadFile = None,
        bucket_name: str = None,
        credentials=None
    ) -> Firmware:
        # Check for duplicate version in org
        if db.query(Firmware).filter_by(
            organisation_id=organisation_id,
            firmware_version=firmware_data["firmware_version"]
        ).first():
            raise HTTPException(status_code=400, detail="Firmware version already exists for this organisation.")

        # Load credentials if not provided
        if credentials is None:
            credentials = load_gcp_credentials()
            if credentials is None:
                raise HTTPException(
                    status_code=500, 
                    detail="Google Cloud Storage credentials not available. Please check your GCP configuration."
                )
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(bucket_name or os.getenv("BUCKET_NAME"))

        firmwareVersion = firmware_data["firmware_version"]
        firmware_string = f'firmware/firmware_file_bin/{firmwareVersion}.bin'
        firmware_string_hex = None
        firmware_string_bootloader = None

        # Read firmware file
        firmware_content = firmware_file.file.read()
        bin_data_for_crc = None
        firmware_bin_size = 0  # Initialize bin size variable
        
        if firmware_file.filename.endswith('.hex'):
            # Convert hex to bin and upload both
            try:
                firmware_content_str = firmware_content.decode('utf-8')
            except UnicodeDecodeError:
                firmware_content_str = firmware_content.decode('ascii', errors='ignore')
            bin_data = io.BytesIO()
            firmware_hex = IntelHex()
            firmware_hex.loadhex(io.StringIO(firmware_content_str))
            firmware_hex.tobinfile(bin_data)
            bin_data.seek(0)
            # Get binary data for CRC32 calculation
            bin_data_for_crc = bin_data.read()
            firmware_bin_size = len(bin_data_for_crc)  # Store bin file size
            bin_data.seek(0)  # Reset for upload
            # Upload bin
            bucket.blob(firmware_string).upload_from_file(bin_data)
            # Upload hex
            firmware_string_hex = f'firmware/firmware_file_hex/{firmwareVersion}.hex'
            bucket.blob(firmware_string_hex).upload_from_string(firmware_content)
        else:
            # For bin files, use the content directly
            bin_data_for_crc = firmware_content
            firmware_bin_size = len(bin_data_for_crc)  # Store bin file size
            # Only upload bin
            bucket.blob(firmware_string).upload_from_string(firmware_content)
        
        # Calculate CRC32 checksum from binary data
        crc32_checksum = format(zlib.crc32(bin_data_for_crc) & 0xffffffff, '08x')

        # Bootloader: always store as-is, no conversion
        if firmware_bootloader:
            firmware_bootloader_content = firmware_bootloader.file.read()
            firmware_string_bootloader = f'firmware/firmware_file_bootloader/{firmwareVersion}.hex'
            bucket.blob(firmware_string_bootloader).upload_from_string(firmware_bootloader_content)

        # Create DB record
        new_firmware = Firmware(
            organisation_id=organisation_id,
            firmware_version=firmware_data["firmware_version"],
            firmware_string=firmware_string,
            firmware_string_hex=firmware_string_hex,
            firmware_string_bootloader=firmware_string_bootloader,
            firmware_type=firmware_data.get("firmware_type", FirmwareType.beta),
            description=firmware_data.get("description"),
            crc32=crc32_checksum,
            firmware_bin_size=firmware_bin_size,  # Add the bin size here
            change1=firmware_data.get("change1"),
            change2=firmware_data.get("change2"),
            change3=firmware_data.get("change3"),
            change4=firmware_data.get("change4"),
            change5=firmware_data.get("change5"),
            change6=firmware_data.get("change6"),
            change7=firmware_data.get("change7"),
            change8=firmware_data.get("change8"),
            change9=firmware_data.get("change9"),
            change10=firmware_data.get("change10"),
        )
        db.add(new_firmware)
        db.commit()
        db.refresh(new_firmware)
        return new_firmware

    @staticmethod
    def get_firmware_by_version(db: Session, organisation_id: uuid.UUID, firmware_version: str) -> Firmware:
        firmware = db.query(Firmware).filter_by(
            organisation_id=organisation_id,
            firmware_version=firmware_version
        ).first()
        if not firmware:
            raise HTTPException(status_code=404, detail="Firmware version not found for this organisation.")
        return firmware

    @staticmethod
    def list_firmwares(db: Session, organisation_id: uuid.UUID):
        return db.query(Firmware).filter_by(organisation_id=organisation_id).all()

    @staticmethod
    def download_firmware_file(
        db: Session,
        organisation_id: uuid.UUID,
        firmware_version: str,
        file_type: str,
        bucket_name: str = None,
        credentials=None,
        range_start: int = None,
        range_end: int = None
    ):
        firmware = FirmwareController.get_firmware_by_version(db, organisation_id, firmware_version)
        if file_type == "bin":
            blob_path = firmware.firmware_string
        elif file_type == "hex":
            blob_path = firmware.firmware_string_hex
        elif file_type == "bootloader":
            blob_path = firmware.firmware_string_bootloader
        else:
            raise HTTPException(status_code=400, detail="Invalid file type requested.")
        if not blob_path:
            raise HTTPException(status_code=404, detail="Requested firmware file not found.")

        # Load credentials if not provided
        if credentials is None:
            credentials = load_gcp_credentials()
            if credentials is None:
                raise HTTPException(
                    status_code=500, 
                    detail="Google Cloud Storage credentials not available. Please check your GCP configuration."
                )
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(bucket_name or os.getenv("BUCKET_NAME"))
        blob = bucket.blob(blob_path)
        blob.reload()
        
        file_size = blob.size
        
        # Handle range requests
        if range_start is not None or range_end is not None:
            # Validate range
            if range_start is None:
                range_start = 0
            if range_end is None:
                range_end = file_size - 1
            
            # Ensure range is valid
            if range_start < 0 or range_end >= file_size or range_start > range_end:
                raise HTTPException(status_code=416, detail=f"Range not satisfiable. File size: {file_size}")
            
            # Download the specified range
            file_data = blob.download_as_bytes(start=range_start, end=range_end + 1)
            return file_data, file_size, blob_path, range_start, range_end
        else:
            # Download entire file
            file_data = blob.download_as_bytes()
            return file_data, file_size, blob_path, None, None

    @staticmethod
    def get_firmware_by_id(db: Session, organisation_id: uuid.UUID, firmware_id: uuid.UUID) -> Firmware:
        firmware = db.query(Firmware).filter_by(
            organisation_id=organisation_id,
            id=firmware_id
        ).first()
        if not firmware:
            raise HTTPException(status_code=404, detail="Firmware not found for this organisation.")
        return firmware

    @staticmethod
    def download_firmware_file_by_id(
        db: Session,
        organisation_id: uuid.UUID,
        firmware_id: uuid.UUID,
        file_type: str,
        bucket_name: str = None,
        credentials=None,
        range_start: int = None,
        range_end: int = None
    ):
        firmware = FirmwareController.get_firmware_by_id(db, organisation_id, firmware_id)
        if file_type == "bin":
            blob_path = firmware.firmware_string
        elif file_type == "hex":
            blob_path = firmware.firmware_string_hex
        elif file_type == "bootloader":
            blob_path = firmware.firmware_string_bootloader
        else:
            raise HTTPException(status_code=400, detail="Invalid file type requested.")
        if not blob_path:
            raise HTTPException(status_code=404, detail="Requested firmware file not found.")

        # Load credentials if not provided
        if credentials is None:
            credentials = load_gcp_credentials()
            if credentials is None:
                raise HTTPException(
                    status_code=500, 
                    detail="Google Cloud Storage credentials not available. Please check your GCP configuration."
                )
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(bucket_name or os.getenv("BUCKET_NAME"))
        blob = bucket.blob(blob_path)
        blob.reload()
        
        file_size = blob.size
        
        # Handle range requests
        if range_start is not None or range_end is not None:
            # Validate range
            if range_start is None:
                range_start = 0
            if range_end is None:
                range_end = file_size - 1
            
            # Ensure range is valid
            if range_start < 0 or range_end >= file_size or range_start > range_end:
                raise HTTPException(status_code=416, detail=f"Range not satisfiable. File size: {file_size}")
            
            # Download the specified range
            file_data = blob.download_as_bytes(start=range_start, end=range_end + 1)
            return file_data, file_size, blob_path, range_start, range_end
        else:
            # Download entire file
            file_data = blob.download_as_bytes()
            return file_data, file_size, blob_path, None, None

    @staticmethod
    def update_firmware_type(
        db: Session,
        organisation_id: uuid.UUID,
        firmware_id: uuid.UUID,
        firmware_type: FirmwareType
    ) -> Firmware:
        firmware = FirmwareController.get_firmware_by_id(db, organisation_id, firmware_id)
        firmware.firmware_type = firmware_type
        db.commit()
        db.refresh(firmware)
        return firmware
