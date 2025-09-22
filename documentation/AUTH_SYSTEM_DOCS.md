# 🔐 Authentication & Authorization System

This document explains the authentication and authorization system implemented in the IoT Hub FastAPI application.

## 🎯 Overview

The system uses JWT (JSON Web Tokens) with embedded organization context for authentication and role-based authorization. Each user gets a single token that contains both user information and organization memberships.

## 🔑 Token Structure

### Login Response
```json
{
  "message": "Login successful",
  "user_id": "f4e32cfb-af73-4e3b-bc82-fed57e8196de",
  "username": "Gibson",
  "email": "gibsonoluka7@gmail.com", 
  "is_admin": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### JWT Token Payload
```json
{
  "user_id": "f4e32cfb-af73-4e3b-bc82-fed57e8196de",
  "email": "gibsonoluka7@gmail.com",
  "is_admin": true,
  "org_ids": ["org1", "org2"],
  "primary_org_id": "org1", 
  "primary_org_role": "admin",
  "org_info": [
    {
      "org_id": "org1",
      "org_name": "Company A",
      "role": "admin",
      "is_active": true
    },
    {
      "org_id": "org2", 
      "org_name": "Company B",
      "role": "user",
      "is_active": true
    }
  ],
  "exp": 1625097600
}
```

## 🛡️ Authorization Rules

### User Endpoints

| Endpoint | Method | Authorization Required |
|----------|--------|----------------------|
| `/login` | POST | None |
| `/logout` | POST | None |
| `/users` | GET | **Admin only** |
| `/users` | POST | **Admin only** |
| `/users/{user_id}` | GET | **Admin OR own data** |

### Organization Endpoints

| Endpoint | Method | Authorization Required |
|----------|--------|----------------------|
| `/organisations` | GET | **Admin only** |
| `/organisations` | POST | **Admin only** |
| `/organisations/{org_id}` | GET | **Admin only** |

## 🔧 Implementation Details

### Security Functions

#### `get_current_user()`
- Validates JWT token from Authorization header
- Extracts user information and organization context
- Returns user object with embedded token data

#### `get_admin_user()`  
- Validates JWT token AND checks `is_admin` flag
- Used for admin-only endpoints
- Raises 403 error if user is not admin

#### `get_current_user_or_admin()`
- Used for endpoints where users can access their own data OR admins can access any data
- Checks if user is admin OR if they're accessing their own user_id

### Usage Examples

#### Admin-Only Endpoint
```python
@router.get("/users", response_model=List[UserRead])
def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # ← Admin required
):
    return UserController.get_all_users(db)
```

#### Self-Access or Admin Endpoint
```python
@router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ← Any authenticated user
):
    # Manual check for self-access or admin
    if not current_user.is_admin and str(current_user.id) != str(user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return UserController.get_user(user_id, db)
```

## 🌐 API Usage

### 1. Login
```bash
POST /login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### 2. Use Token for Protected Endpoints
```bash
GET /users
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 3. Error Responses

#### 401 Unauthorized (No/Invalid Token)
```json
{
  "detail": "Invalid authorization header format. Use 'Bearer <token>'"
}
```

#### 403 Forbidden (Insufficient Permissions)
```json
{
  "detail": "Admin privileges required."
}
```

## 🔄 Token Flow

```
1. User logs in with email/password
2. Server validates credentials
3. Server creates JWT with user + org context
4. Client stores token
5. Client sends token in Authorization header
6. Server validates token and extracts user context
7. Server checks permissions based on endpoint requirements
8. Server allows/denies access
```

## 🛠️ Organization Context Features

The JWT token includes organization context which enables:

- **Fast authorization checks** (no database queries)
- **Multi-tenant support** (user belongs to multiple orgs)
- **Role-based access control** (admin/manager/user roles per org)
- **Organization-scoped data access** (future feature)

### Accessing Organization Data

```python
# In your endpoint function
def some_endpoint(current_user = Depends(get_current_user)):
    # Access organization IDs
    org_ids = current_user.token_org_ids
    
    # Access primary organization
    primary_org = current_user.token_primary_org_id
    
    # Access detailed org info
    org_info = current_user.token_org_info
    
    # Check if user belongs to specific org
    if "specific-org-id" in org_ids:
        # User has access to this organization
        pass
```

## 🔒 Security Considerations

1. **Token Expiration**: Tokens expire after 1 hour by default
2. **Blacklisting**: Logout adds tokens to blacklist (in-memory, use Redis in production)
3. **Organization Changes**: Users need to re-login to get updated org memberships
4. **Admin Privileges**: Global admin flag allows access to all endpoints
5. **HTTPS Only**: Always use HTTPS in production for token security

## 🧪 Testing

Use the provided test scripts:
- `test_auth_system.py` - Tests the complete auth flow
- `test_enhanced_login.py` - Tests token structure and JWT payload

```bash
# Run authentication tests
python test_auth_system.py
```

## 🚀 Next Steps

1. **Organization-Scoped Endpoints**: Add endpoints that filter data by organization membership
2. **Role-Based Access**: Implement fine-grained permissions based on organization roles
3. **Token Refresh**: Add token refresh mechanism for long-running sessions
4. **Audit Logging**: Log authentication and authorization events
5. **Rate Limiting**: Add rate limiting to prevent brute force attacks
