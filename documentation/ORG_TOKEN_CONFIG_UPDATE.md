# Org Token Config Update Endpoint

## Overview
A new endpoint has been added to update device configuration using organization token authentication.

## Endpoint Details

**URL:** `/api/v1/device_data/config/{org_token}/{deviceID}/update`  
**Method:** `POST`  
**Authentication:** Organization Token (no JWT required)

## Parameters

### Path Parameters
- `org_token` (string): Organization token from the `organisations` table
- `deviceID` (integer): The device ID to update configuration for

### Request Body
```json
{
  "config1": "value1",
  "config2": "value2",
  "config3": "value3",
  // ... up to config10
}
```

Note: You can provide any subset of config1-config10. Missing configs will preserve their existing values.

## Response

### Success (200 OK)
```json
{
  "deviceID": 123,
  "fileDownloadState": false,
  "config_updated": true,
  "configs": {
    "config1": "value1",
    "config2": "value2",
    "config3": "value3",
    // ... all non-null configs
  }
}
```

### Error Responses

**404 - Invalid Organization Token**
```json
{
  "detail": "Invalid organization token!"
}
```

**404 - Device Not Found**
```json
{
  "detail": "Device not found!"
}
```

**403 - Device Not in Organization**
```json
{
  "detail": "Device does not belong to your organization!"
}
```

## Security Features

1. **Organization Validation**: Validates the org_token against the `organisations` table
2. **Device Ownership**: Ensures the device belongs to the organization through the profile relationship
3. **No JWT Required**: Uses direct org_token validation instead of JWT authentication

## Data Flow

1. Validates `org_token` → gets `organisation_id`
2. Finds device by `deviceID`
3. Gets device's profile and verifies `profile.organisation_id` matches
4. Creates new `ConfigValues` entry with `config_updated=True`
5. Returns latest configuration

## Database Relations

```
Organisation → Profile → Device → ConfigValues
```

The endpoint ensures that only devices belonging to the specified organization can be updated.

## Usage Example

```bash
curl -X POST "http://localhost:8000/api/v1/device_data/config/abc123token/456/update" \
  -H "Content-Type: application/json" \
  -d '{
    "config1": "new_temperature_threshold", 
    "config2": "updated_interval",
    "config5": "enabled"
  }'
```

## Key Features

- ✅ No JWT authentication required - only org_token
- ✅ Automatically sets `config_updated=True`
- ✅ Returns the latest complete configuration
- ✅ Preserves existing config values not specified in request
- ✅ Validates device ownership by organization
- ✅ Creates new config entry (maintains history)