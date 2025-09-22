#!/usr/bin/env python3
"""
Debug JWT token to check what's inside and validate it.
"""

import jwt
import json
from datetime import datetime

# Your JWT token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjRlMzJjZmItYWY3My00ZTNiLWJjODItZmVkNTdlODE5NmRlIiwiZW1haWwiOiJnaWJzb25vbHVrYTdAZ21haWwuY29tIiwiaXNfYWRtaW4iOnRydWUsIm9yZ19pZHMiOlsiNzE0YzdiOTktZjFkZC00ZWMxLThkZmItNDAwYjZmZjNmN2JmIl0sInByaW1hcnlfb3JnX2lkIjoiNzE0YzdiOTktZjFkZC00ZWMxLThkZmItNDAwYjZmZjNmN2JmIiwicHJpbWFyeV9vcmdfcm9sZSI6ImFkbWluIiwib3JnX2luZm8iOlt7Im9yZ19pZCI6IjcxNGM3Yjk5LWYxZGQtNGVjMS04ZGZiLTQwMGI2ZmYzZjdiZiIsIm9yZ19uYW1lIjoiSW9USHViIiwicm9sZSI6ImFkbWluIiwiaXNfYWN0aXZlIjp0cnVlfV0sImV4cCI6MTc1NzUxNTk2N30.7afTU72PDHuC6bLHbtToLxYRiBeUEJh1n2vUlqCTqhs"

# Default JWT secret (as used in your code)
JWT_SECRET = "your_secret_key"
JWT_ALGORITHM = "HS256"

def debug_jwt_token():
    print("🔍 JWT Token Debug")
    print("=" * 50)
    
    try:
        # Decode without verification first to see the payload
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        print("✅ Token payload (unverified):")
        print(json.dumps(unverified_payload, indent=2))
        
        # Check expiration
        exp_timestamp = unverified_payload.get('exp')
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            current_datetime = datetime.now()
            print(f"\n📅 Token expiration:")
            print(f"   Expires at: {exp_datetime}")
            print(f"   Current time: {current_datetime}")
            print(f"   Valid: {'✅ Yes' if exp_datetime > current_datetime else '❌ Expired'}")
        
        # Try to decode with verification
        print(f"\n🔐 Verifying with secret: '{JWT_SECRET}'")
        verified_payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print("✅ Token is valid and verified!")
        
        # Check admin status
        is_admin = verified_payload.get('is_admin', False)
        print(f"\n👤 User info:")
        print(f"   User ID: {verified_payload.get('user_id')}")
        print(f"   Email: {verified_payload.get('email')}")
        print(f"   Is Admin: {'✅ Yes' if is_admin else '❌ No'}")
        print(f"   Org IDs: {verified_payload.get('org_ids', [])}")
        
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
    except jwt.InvalidSignatureError:
        print("❌ Invalid token signature - wrong secret key")
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_api_endpoints():
    print(f"\n🌐 API Endpoint Testing")
    print("=" * 50)
    
    import requests
    
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different endpoint paths
    endpoints_to_test = [
        "/users",           # Wrong path (no prefix)
        "/api/v1/users",    # Correct path (with prefix)
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code != 200:
                error_detail = response.json().get("detail", "No detail") if response.text else "No response"
                print(f"      Error: {error_detail}")
        except requests.exceptions.ConnectionError:
            print(f"   {endpoint}: Could not connect to server")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

if __name__ == "__main__":
    debug_jwt_token()
    test_api_endpoints()
    
    print(f"\n💡 Solution:")
    print("1. Use the correct endpoint: /api/v1/users (not /users)")
    print("2. Ensure your server is running on localhost:8000")
    print("3. Use the authorization header: Bearer <your_token>")
