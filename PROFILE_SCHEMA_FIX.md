# Profile Schema Fix - config_updated Boolean Support

## Issue
The profile endpoint was failing with a 500 error when trying to return the `config_updated` field in the `recent_config` object of devices. The error was:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for DeviceConfigSummary
recent_config.config_updated
  Input should be a valid string [type=string_type, input_value=True, input_type=bool]
```

## Root Cause
The `DeviceConfigSummary` schema in `schemas/profile.py` was defined with:

```python
class DeviceConfigSummary(BaseModel):
    name: str
    deviceID: str
    recent_config: Dict[str, Optional[str]]  # ← Only allowed strings
```

This meant all values in `recent_config` had to be strings, but we were trying to add a boolean `config_updated` field.

## Solution
Updated the schema to support both strings and booleans in the `recent_config` dictionary:

### Before:
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
import datetime

class DeviceConfigSummary(BaseModel):
    name: str
    deviceID: str
    recent_config: Dict[str, Optional[str]]  # ← Only strings
```

### After:
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union  # ← Added Union
from uuid import UUID
import datetime

class DeviceConfigSummary(BaseModel):
    name: str
    deviceID: str
    recent_config: Dict[str, Union[str, bool, None]]  # ← Now supports strings, booleans, and None
```

## Changes Made

1. **Added Union import** - Import `Union` from typing
2. **Updated type annotation** - Changed `Dict[str, Optional[str]]` to `Dict[str, Union[str, bool, None]]`

## Result

The profile endpoint (`GET /api/v1/profiles/{profile_id}`) now correctly returns:

```json
{
    "devices": [
        {
            "name": "test1",
            "deviceID": "1",
            "recent_config": {
                "config_updated": true,  // ← Boolean works now
                "config1": "1",          // ← Strings still work
                "config2": "2"           // ← Strings still work
            }
        }
    ]
}
```

## Validation

- ✅ Schema accepts boolean `config_updated` field
- ✅ Schema still accepts string config values
- ✅ Schema handles `None` values
- ✅ Empty config dictionaries work
- ✅ Server imports successfully
- ✅ Profile controller works without errors

## Files Modified

- `schemas/profile.py` - Updated `DeviceConfigSummary` schema type annotations

This fix ensures that the profile endpoint can successfully return the `config_updated` boolean field alongside the existing string config values.