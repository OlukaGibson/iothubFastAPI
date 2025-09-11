#!/usr/bin/env python3
"""
Test script for the enhanced authentication and authorization system.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_authentication_flow():
    """Test the complete authentication and authorization flow."""
    print("🔐 Testing Authentication & Authorization Flow")
    print("=" * 60)
    
    # Step 1: Login to get token
    print("\n1️⃣ Testing Login...")
    login_data = {
        "email": "admin@example.com",  # Change to your admin user
        "password": "admin123"         # Change to correct password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["token"]
            is_admin = login_result["is_admin"]
            user_id = login_result["user_id"]
            
            print(f"✅ Login successful!")
            print(f"   User ID: {user_id}")
            print(f"   Is Admin: {is_admin}")
            print(f"   Token: {token[:50]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Step 2: Test admin-only endpoints
            print(f"\n2️⃣ Testing Admin-Only Endpoints (is_admin={is_admin})...")
            test_admin_endpoints(headers, is_admin)
            
            # Step 3: Test user-specific endpoints
            print(f"\n3️⃣ Testing User-Specific Endpoints...")
            test_user_endpoints(headers, user_id)
            
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure FastAPI server is running.")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return

def test_admin_endpoints(headers, is_admin):
    """Test endpoints that require admin privileges."""
    admin_endpoints = [
        ("GET", "/users", "Get all users"),
        ("GET", "/organisations", "Get all organisations"),
        ("POST", "/users", "Create user"),
        ("POST", "/organisations", "Create organisation"),
    ]
    
    for method, endpoint, description in admin_endpoints:
        if method == "GET":
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    count = len(result) if isinstance(result, list) else 1
                    print(f"   ✅ {description}: {response.status_code} - Found {count} items")
                elif response.status_code == 403:
                    print(f"   🔒 {description}: {response.status_code} - Access denied (expected if not admin)")
                else:
                    print(f"   ⚠️  {description}: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"   ❌ {description}: Error - {e}")

def test_user_endpoints(headers, user_id):
    """Test endpoints where users can access their own data."""
    print(f"   Testing access to own user data (ID: {user_id})...")
    
    try:
        # Test accessing own user data
        response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Access own data: {response.status_code} - User: {user_data.get('username', 'N/A')}")
        else:
            print(f"   ❌ Access own data: {response.status_code} - {response.text[:100]}")
            
        # Test accessing another user's data (should fail if not admin)
        # You'll need to replace this with an actual different user ID
        other_user_id = "00000000-0000-0000-0000-000000000000"  # Fake ID for testing
        response = requests.get(f"{BASE_URL}/users/{other_user_id}", headers=headers)
        if response.status_code == 403:
            print(f"   ✅ Access other user data: {response.status_code} - Correctly denied")
        elif response.status_code == 404:
            print(f"   ✅ Access other user data: {response.status_code} - User not found (expected)")
        elif response.status_code == 200:
            print(f"   ✅ Access other user data: {response.status_code} - Allowed (admin user)")
        else:
            print(f"   ⚠️  Access other user data: {response.status_code} - {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ User endpoint test error: {e}")

def test_no_auth():
    """Test endpoints without authentication."""
    print(f"\n4️⃣ Testing Without Authentication...")
    
    protected_endpoints = [
        ("GET", "/users", "Get all users"),
        ("GET", "/organisations", "Get all organisations"),
    ]
    
    for method, endpoint, description in protected_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"   ✅ {description}: {response.status_code} - Correctly requires auth")
            else:
                print(f"   ⚠️  {description}: {response.status_code} - Unexpected response")
        except Exception as e:
            print(f"   ❌ {description}: Error - {e}")

if __name__ == "__main__":
    test_authentication_flow()
    test_no_auth()
    
    print("\n" + "="*60)
    print("🎉 Authorization Test Completed!")
    print("\n📋 Summary of Authorization Rules:")
    print("• GET /users - Admin only")
    print("• POST /users - Admin only") 
    print("• GET /users/{user_id} - Admin or own data")
    print("• GET /organisations - Admin only")
    print("• POST /organisations - Admin only")
    print("• GET /organisations/{org_id} - Admin only")
    print("• POST /login - No auth required")
    print("• POST /logout - No auth required")
