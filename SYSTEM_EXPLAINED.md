# IoTHub FastAPI System Architecture & Workflow

This document provides a detailed explanation of how the IoTHub FastAPI backend operates, describing its architecture, main flows, and the responsibilities of each component.

---

## 1. Overview

IoTHub FastAPI is a backend system for managing IoT devices, users, organisations, firmware, and device data. It is built with FastAPI (for REST APIs), SQLAlchemy (for ORM/database), and integrates with Google Cloud Storage for firmware management. The system is modular, scalable, and secure.

---

## 2. Main Components

### Users & Organisations

- **Users**: Individuals who interact with the system. Each user has credentials and can belong to one or more organisations.
- **Organisations**: Logical groups for users and devices. Organisations enable role-based access and device grouping.

**Flow**:
- Users register via `/api/v1/users`.
- Organisations are created via `/api/v1/organisations`.
- Users can be linked to organisations, and roles/permissions can be managed.

### Devices

- **Devices**: Physical IoT units registered in the system. Each device has a unique `deviceID`, `readkey`, and `writekey` for secure communication.
- **Profiles**: Templates that define the structure of device data, metadata, and config values. Devices are assigned to profiles for flexible configuration.

**Flow**:
- Devices are registered via `/api/v1/device`.
- Devices are linked to organisations and profiles.
- Device keys are used for secure data/config ingestion.

### Device Data, Metadata, Configs

- **Device Data**: Sensor readings or other data sent by devices.
- **Metadata**: Additional information about device state or environment.
- **Config Values**: Configuration parameters sent to or from devices.

**Flow**:
- Devices send data via `/api/v1/device_data/update` or bulk endpoints.
- Metadata and config updates are handled via `/api/v1/metadata/update` and `/api/v1/config/update`.
- Data is stored in structured tables for querying and analysis.

### Firmware Management

- **Firmware**: Binary files for device updates, stored in Google Cloud Storage.
- **Firmware Versioning**: Devices track current, previous, and target firmware versions.

**Flow**:
- Firmware is uploaded via `/api/v1/firmware/upload`.
- Devices request firmware updates via `/api/v1/device/{deviceID}/update_firmware`.
- Firmware files are downloaded securely from GCS.

### Authentication & Security

- **Password Hashing**: User passwords are securely hashed.
- **Token-Based Auth**: Users and devices use tokens/keys for authentication.
- **Role Management**: Admin endpoints are protected; only authorized users can perform certain actions.

---

## 3. Data Model & Database

- **SQLAlchemy Models**: Each domain (user, organisation, device, profile, data, metadata, config, firmware) has a corresponding SQLAlchemy model.
- **Relationships**: Devices belong to organisations and profiles; users belong to organisations.
- **Extensibility**: Profiles allow dynamic field/config/metadata definitions for different device types.

---

## 4. API Layer

- **FastAPI**: Exposes REST endpoints for all operations.
- **Pydantic Schemas**: Used for request/response validation.
- **Controllers**: Business logic for each domain.
- **Routes**: Organised by domain for clarity and maintainability.

---

## 5. Typical Workflows

### Device Registration

1. Admin/user registers a device via `/api/v1/device`.
2. Device is assigned to an organisation and profile.
3. Device keys are generated for secure communication.

### Data Ingestion

1. Device sends data to `/api/v1/device_data/update` using its writekey.
2. Data is validated and stored in the database.
3. Metadata/config updates follow similar flows.

### Firmware Update

1. Admin uploads new firmware via `/api/v1/firmware/upload`.
2. Device requests update via `/api/v1/device/{deviceID}/update_firmware`.
3. System checks version, updates device record, and provides download link.

### User & Organisation Management

1. Users register and are linked to organisations.
2. Admins manage organisations and assign roles.
3. Users can view and manage devices within their organisation.

---

## 6. Extensibility & Maintenance

- **Modular Codebase**: Organised into `models/`, `schemas/`, `controllers/`, `routes/`, `utils/`.
- **Alembic Migrations**: Used for database schema changes.
- **Environment Variables**: All secrets and configs are managed via `.env`.

---

## 7. Security Considerations

- All sensitive endpoints require authentication.
- Device keys and tokens are unique and securely generated.
- Passwords are hashed using industry-standard algorithms.
- Role-based access restricts admin operations.

---

## 8. Integration Points

- **Google Cloud Storage**: For firmware file storage and retrieval.
- **PostgreSQL**: Recommended database backend for reliability and scalability.

---

## 9. Error Handling & Validation

- All API requests are validated using Pydantic schemas.
- Errors are returned with clear messages and status codes.
- Database constraints ensure data integrity.

---

## 10. Summary

IoTHub FastAPI provides a robust backend for IoT device management, supporting secure registration, data ingestion, firmware updates, and flexible configuration. Its modular design and extensibility make it suitable for a wide range of IoT applications.

