from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from utils.database_config import get_db
import uuid
import jwt
import os
from typing import Optional

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    from models.user_org import User
    
    # Debug: Print what we received
    # print(f"🔍 DEBUG - Authorization header received: {repr(authorization)}")
    
    # Check if authorization header is provided
    if not authorization:
        # print("❌ DEBUG - No authorization header provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required. Please provide a valid token.",
        )
    
    # Extract token from Bearer header
    if not authorization.startswith("Bearer "):
        # print(f"❌ DEBUG - Invalid format. Expected 'Bearer <token>', got: {repr(authorization)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
        )
    
    token = authorization.split(" ")[1]
    # print(f"🔑 DEBUG - Token extracted: {token[:50]}..." if len(token) > 50 else f"🔑 DEBUG - Token extracted: {token}")
    
    # Check if token is blacklisted (logged out)
    # Note: Using a simple in-memory blacklist for now
    # In production, use Redis or database
    try:
        from routes.user_org import jwt_blacklist
        if token in jwt_blacklist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated. Please login again.",
            )
    except ImportError:
        # Handle case where blacklist is not available
        pass
    
    try:
        # Decode JWT token
        # print(f"🔐 DEBUG - Attempting to decode JWT with secret: {JWT_SECRET[:10]}...")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        # print(f"✅ DEBUG - JWT decoded successfully. User ID: {user_id}")
        
        if user_id is None:
            # print("❌ DEBUG - No user_id in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # Attach organization context from JWT if available (for org tokens)
        user.token_org_ids = payload.get("org_ids", [])
        user.token_primary_org_id = payload.get("primary_org_id")
        user.token_primary_org_role = payload.get("primary_org_role")
        user.token_org_info = payload.get("org_info", [])
        user.token_type = "org" if payload.get("org_ids") else "basic"
        
        return user
        
    except jwt.ExpiredSignatureError as e:
        # print(f"❌ DEBUG - Token expired: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        # print(f"❌ DEBUG - Invalid token error: {e}")
        # print(f"❌ DEBUG - Token that failed: {token[:100]}..." if len(token) > 100 else f"❌ DEBUG - Token that failed: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

def get_user_with_org_context(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get current user and ensure organization context is available.
    This function requires an org token (JWT with organization information).
    """
    user = get_current_user(authorization, db)
    
    if not hasattr(user, 'token_type') or user.token_type != "org":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization context required. Please use an organization token.",
        )
    
    if not user.token_org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization.",
        )
    
    return user

def check_org_access(user, org_id: str) -> bool:
    """
    Check if user has access to a specific organization based on JWT token.
    """
    if not hasattr(user, 'token_org_ids'):
        return False
    
    return str(org_id) in user.token_org_ids

def get_user_role_in_org(user, org_id: str) -> Optional[str]:
    """
    Get user's role in a specific organization from JWT token.
    """
    if not hasattr(user, 'token_org_info'):
        return None
    
    for org_info in user.token_org_info:
        if org_info.get("org_id") == str(org_id):
            return org_info.get("role")
    
    return None

def get_admin_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get current user and ensure they have admin privileges.
    This function requires the user to be an admin.
    """
    user = get_current_user(authorization, db)
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    
    return user

def get_current_user_or_admin(
    user_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get current user and ensure they are either an admin or the user themselves.
    Used for endpoints where users can access their own data or admins can access any data.
    """
    user = get_current_user(authorization, db)
    
    # Allow if user is admin or if they're accessing their own data
    if user.is_admin or str(user.id) == str(user_id):
        return user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: You can only access your own data or must be an admin.",
    )
