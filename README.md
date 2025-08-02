# IoTHub FastAPI Backend

A scalable backend API for IoTHub, built with FastAPI and SQLAlchemy, supporting device management, firmware updates, user and organisation management, and more.

## Features

- User and Organisation management (registration, linking, roles)
- Device registration, configuration, and data ingestion
- Firmware upload/download with Google Cloud Storage integration
- Profile management for device templates/configs
- Secure authentication and password hashing
- Bulk and individual device data/config updates
- Extensible metadata and config value models

## Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy (PostgreSQL recommended)
- Alembic (for migrations)
- Google Cloud Storage (for firmware files)
- Pydantic (for schema validation)
- Passlib (for password hashing)
- Uvicorn (ASGI server)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/iothubFastAPI.git
cd iothubFastAPI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your database, GCP, and admin credentials:

```env
DATABASE_URL='postgresql://user:password@host:port/dbname'
BUCKET_NAME=your-gcs-bucket
GOOGLE_APPLICATION_CREDENTIALS_JSON={...}
ADMIN_EMAIL='admin@example.com'
ADMIN_PASSWORD='yourpassword'
ADMIN_USERNAME='adminuser'
ADMIN_ORGANISATION='DefaultOrg'
```

### 4. Run database migrations (optional)

If using Alembic:

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### User & Organisation

- `POST /api/v1/users` - Register a new user
- `GET /api/v1/users/{user_id}` - Get user details
- `GET /api/v1/users` - List all users
- `POST /api/v1/organisations` - Create organisation (admin only)
- `GET /api/v1/organisations/{org_id}` - Get organisation details
- `GET /api/v1/organisations` - List all organisations

### Device

- `POST /api/v1/device` - Register a device
- `GET /api/v1/device` - List devices
- `GET /api/v1/device/{deviceID}` - Get device details
- `PUT /api/v1/device/{deviceID}` - Update device
- `POST /api/v1/device/{deviceID}/update_firmware` - Update device firmware
- `GET /api/v1/device/network/{networkID}/selfconfig` - Get device self-config

### Device Data

- `POST /api/v1/device_data/update` - Update device data
- `POST /api/v1/device_data/bulk_update/{deviceID}` - Bulk update device data
- `POST /api/v1/metadata/update` - Update device metadata
- `POST /api/v1/config/update` - Update device config
- `POST /api/v1/config/mass_edit` - Mass edit device configs
- `GET /api/v1/config/{deviceID}` - Get device config

### Firmware

- `POST /api/v1/firmware/upload` - Upload firmware (bin/hex/bootloader)
- `GET /api/v1/firmware` - List firmwares
- `GET /api/v1/firmware/{firmware_id}` - Get firmware details
- `GET /api/v1/firmware/{firmware_id}/download/{file_type}` - Download firmware file

### Profile

- `POST /api/v1/profiles` - Create device profile
- `GET /api/v1/profiles` - List profiles
- `GET /api/v1/profiles/{profile_id}` - Get profile details

## Environment Variables

See `.env` for all required variables. Key ones:

- `DATABASE_URL` - SQLAlchemy DB connection string
- `BUCKET_NAME` - GCP bucket for firmware files
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` - GCP service account JSON
- `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_USERNAME`, `ADMIN_ORGANISATION` - Default admin credentials

## Development

- Code is organized by domain: `models/`, `schemas/`, `controllers/`, `routes/`, `utils/`
- Use Alembic for migrations if you change models
- All API responses use Pydantic schemas for validation

## Contributing

1. Fork the repo and create your branch
2. Make changes with clear commit messages
3. Ensure code passes linting and tests
4. Submit a pull request

## License

MIT License

---

For questions or support, open an issue or contact the [Gibson Oluka](http://github.com/OlukaGibson)
To reach me on other socials
[x.com](https://x.com/OlsGibson)
[youtube](https://www.youtube.com/@theemusicNmovies)
[insta](https://www.instagram.com/olsgibson/)