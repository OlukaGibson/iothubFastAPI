#!/usr/bin/env python3
"""
Quick test to verify authentication is properly enforced.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_no_auth_protection():
    """Test that endpoints are properly protected when no auth is provided."""
    print("🔒 Testing Authentication Enforcement")
    print("=" * 50)
    
    protected_endpoints = [
        ("GET", "/users", "Get all users"),
        ("GET", "/organisations", "Get all organisations"),
        ("POST", "/users", "Create user"),
        ("POST", "/organisations", "Create organisation"),
    ]
    
    print("Testing endpoints WITHOUT authentication...")
    print("-" * 50)
    
    for method, endpoint, description in protected_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                # Send dummy data for POST requests
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            
            if response.status_code == 401:
                print(f"✅ {description}: {response.status_code} - Correctly requires authentication")
                error_detail = response.json().get("detail", "")
                print(f"   Error: {error_detail}")
            elif response.status_code == 422:
                print(f"✅ {description}: {response.status_code} - Validation error (expected for POST)")
            else:
                print(f"❌ {description}: {response.status_code} - SECURITY ISSUE: Should require auth!")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Could not connect to server")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    print("\n" + "=" * 50)
    print("Testing with INVALID token...")
    print("-" * 50)
    
    # Test with invalid token
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    
    for method, endpoint, description in protected_endpoints[:2]:  # Test first 2 GET endpoints
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=invalid_headers)
            
            if response.status_code == 401:
                print(f"✅ {description}: {response.status_code} - Correctly rejects invalid token")
                error_detail = response.json().get("detail", "")
                print(f"   Error: {error_detail}")
            else:
                print(f"❌ {description}: {response.status_code} - SECURITY ISSUE: Should reject invalid token!")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ {description}: Error - {e}")

def test_with_valid_auth():
    """Test that endpoints work with valid authentication."""
    print("\n" + "=" * 50)
    print("Testing with VALID authentication...")
    print("-" * 50)
    
    # First try to login
    login_data = {
        "email": "admin@example.com",  # Change to your test user
        "password": "admin123"         # Change to correct password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["token"]
            is_admin = login_result["is_admin"]
            
            print(f"✅ Login successful! Admin: {is_admin}")
            
            # Test protected endpoint with valid token
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Get users with valid token: {response.status_code} - Found {len(users)} users")
            elif response.status_code == 403:
                print(f"✅ Get users with valid token: {response.status_code} - Access denied (user not admin)")
            else:
                print(f"⚠️  Get users with valid token: {response.status_code} - {response.text[:100]}")
                
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            print("   Cannot test with valid auth without successful login")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server for login test")
    except Exception as e:
        print(f"❌ Login test error: {e}")

if __name__ == "__main__":
    test_no_auth_protection()
    test_with_valid_auth()
    
    print("\n" + "=" * 50)
    print("🎉 Authentication Test Complete!")
    print("\n💡 Expected Results:")
    print("• All protected endpoints should return 401 without auth")
    print("• All protected endpoints should return 401 with invalid token")
    print("• Protected endpoints should work with valid admin token")
    print("• Non-admin users should get 403 for admin-only endpoints")
