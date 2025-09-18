# IoTHub FastAPI API Endpoints

This document lists all available API endpoints in the IoTHub FastAPI backend, grouped by domain, with a brief description of each.

---

## User & Organisation

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/users` | POST | Register a new user |
| `/api/v1/users/{user_id}` | GET | Get user details |
| `/api/v1/users` | GET | List all users |
| `/api/v1/organisations` | POST | Create organisation (admin only) |
| `/api/v1/organisations/{org_id}` | GET | Get organisation details |
| `/api/v1/organisations` | GET | List all organisations |

---

## Device

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/device` | POST | Register a device |
| `/api/v1/device` | GET | List devices |
| `/api/v1/device/{deviceID}` | GET | Get device details |
| `/api/v1/device/{deviceID}` | PUT | Update device |
| `/api/v1/device/{deviceID}/update_firmware` | POST | Update device firmware |
| `/api/v1/device/network/{networkID}/selfconfig` | GET | Get device self-config |

---

## Device Data

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/device_data/update` | POST | Update device data |
| `/api/v1/device_data/bulk_update/{deviceID}` | POST | Bulk update device data |
| `/api/v1/metadata_update` | GET | Update device metadata with meta1-meta15 parameters and return status |
| `/api/v1/config/update` | POST | Update device config |
| `/api/v1/config/mass_edit` | POST | Mass edit device configs |
| `/api/v1/config/{deviceID}` | GET | Get device config |

---

## Firmware

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/firmware/upload` | POST | Upload firmware (bin/hex/bootloader) |
| `/api/v1/firmware` | GET | List firmwares |
| `/api/v1/firmware/{firmware_id}` | GET | Get firmware details |
| `/api/v1/firmware/{firmware_id}/download/{file_type}` | GET | Download firmware file |

---

## Profile

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/profiles` | POST | Create device profile |
| `/api/v1/profiles` | GET | List profiles |
| `/api/v1/profiles/{profile_id}` | GET | Get profile details |

---

## Notes

- All endpoints are prefixed with `/api/v1`.
- Authentication may be required for some endpoints.
- See the main README for environment variables and setup instructions.

