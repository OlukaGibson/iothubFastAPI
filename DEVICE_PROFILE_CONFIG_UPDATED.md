# Config Updated Field - Device & Profile Routes Update

## Overview
Updated the device detail and profile detail endpoints to include the `config_updated` boolean field in their configuration data responses.

## Updated Endpoints

### 1. GET `/api/v1/device/{deviceID}`
**Location:** `controllers/device.py` - `DeviceController.get_device()`

**Changes Made:**
- Added `config_updated` field to each config entry in the `config_data` array
- Each config entry now includes the boolean field from the `ConfigValues` model

**Updated Response Structure:**
```json
{
    "id": "f33f5ed4-a976-487e-b404-3fc84f7c5e8f",
    "created_at": "2025-09-11T04:36:51.114867",
    "name": "test1",
    "readkey": "HKWJ72LOXBY1RMGG",
    "writekey": "MCBD5Q78E9IKCCK1",
    "deviceID": 1,
    "profile": "1f3e0ddc-acbd-4782-bc39-6805a2df0874",
    "profile_name": "low cost devices",
    "currentFirmwareVersion": "v1trial",
    "targetFirmwareVersion": null,
    "previousFirmwareVersion": null,
    "networkID": "12345",
    "fileDownloadState": false,
    "firmwareDownloadState": "updated",
    "device_data": [],
    "config_data": [
        {
            "entryID": "3ebf5766-ec58-4049-af31-0ca62408c1f3",
            "created_at": "2025-09-16T10:26:04.306779",
            "config_updated": true,  // ← NEW FIELD
            "config1": "1",
            "config2": "2"
        },
        {
            "entryID": "3dba552f-0d10-4210-b6d1-d5bb16c913fa", 
            "created_at": "2025-09-16T10:25:29.469717",
            "config_updated": false,  // ← NEW FIELD
            "config1": "1",
            "config2": "2"
        }
    ],
    "meta_data": [],
    "field_names": {
        "field1": "Temperature",
        "field2": "Humidity", 
        "field3": "Pm 2.5"
    },
    "config_names": {
        "config1": "Sample rate",
        "config2": "Post rate"
    },
    "metadata_names": {
        "metadata1": "Rtc health",
        "metadata2": "PM sensor health"
    }
}
```

### 2. GET `/api/v1/profiles/{profile_id}`
**Location:** `controllers/profile.py` - `ProfileController.get_profile()`

**Changes Made:**
- Added `config_updated` field to the `recent_config` object for each device
- The field comes from the most recent `ConfigValues` entry for each device

**Updated Response Structure:**
```json
{
    "name": "low cost devices",
    "description": "This is for the local devices",
    "fields": {
        "field1": "Temperature",
        "field2": "Humidity",
        "field3": "Pm 2.5"
    },
    "configs": {
        "config1": "Sample rate",
        "config2": "Post rate"
    },
    "metadata": {
        "metadata1": "Rtc health",
        "metadata2": "PM sensor health"
    },
    "id": "1f3e0ddc-acbd-4782-bc39-6805a2df0874",
    "organisation_id": "714c7b99-f1dd-4ec1-8dfb-400b6ff3f7bf",
    "created_at": "2025-09-03T06:43:30.341083", 
    "device_count": 1,
    "devices": [
        {
            "name": "test1",
            "deviceID": "1",
            "recent_config": {
                "config_updated": true,  // ← NEW FIELD
                "config1": "1",
                "config2": "2"
            }
        }
    ]
}
```

## Technical Implementation

### Device Controller Changes
**File:** `controllers/device.py`
**Method:** `get_device()`
**Lines Modified:** ~151-159

```python
# BEFORE
for data in config_data:
    data_dict = {
        'entryID': data.id,
        'created_at': data.created_at,
    }
    for i in range(1, 11):
        val = getattr(data, f'config{i}', None)
        if val:
            data_dict[f'config{i}'] = val
    config_data_list.append(data_dict)

# AFTER
for data in config_data:
    data_dict = {
        'entryID': data.id,
        'created_at': data.created_at,
        'config_updated': data.config_updated,  # ← Added
    }
    for i in range(1, 11):
        val = getattr(data, f'config{i}', None)
        if val:
            data_dict[f'config{i}'] = val
    config_data_list.append(data_dict)
```

### Profile Controller Changes  
**File:** `controllers/profile.py`
**Method:** `get_profile()`
**Lines Modified:** ~93-103

```python
# BEFORE
for device in devices:
    recent_config = db.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by(ConfigValues.created_at.desc()).first()
    config_values = {}
    if recent_config:
        for i in range(1, 11):
            val = getattr(recent_config, f'config{i}', None)
            if val:
                config_values[f'config{i}'] = val

# AFTER  
for device in devices:
    recent_config = db.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by(ConfigValues.created_at.desc()).first()
    config_values = {}
    if recent_config:
        config_values['config_updated'] = recent_config.config_updated  # ← Added
        for i in range(1, 11):
            val = getattr(recent_config, f'config{i}', None)
            if val:
                config_values[f'config{i}'] = val
```

## Benefits

1. **Consistent API**: Both endpoints now provide `config_updated` information
2. **Historical Tracking**: Device endpoint shows `config_updated` for all config history entries
3. **Quick Status Check**: Profile endpoint shows current `config_updated` status for each device
4. **Backward Compatible**: All existing fields remain unchanged

## Related Changes

This complements the previous updates to all config-specific endpoints:
- `GET /api/v1/config/{deviceID}`
- `POST /api/v1/config/update` 
- `POST /api/v1/config/mass_edit`
- `POST /api/v1/config/{org_token}/{deviceID}/update`
- `GET /api/v1/device/network/{org_token}/{networkID}/selfconfig`

All configuration-related endpoints now consistently return the `config_updated` boolean field.