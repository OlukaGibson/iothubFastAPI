#!/usr/bin/env python3
"""
Test authentication with the correct API path and debug any issues.
"""

import requests
import json

# Your JWT token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjRlMzJjZmItYWY3My00ZTNiLWJjODItZmVkNTdlODE5NmRlIiwiZW1haWwiOiJnaWJzb25vbHVrYTdAZ21haWwuY29tIiwiaXNfYWRtaW4iOnRydWUsIm9yZ19pZHMiOlsiNzE0YzdiOTktZjFkZC00ZWMxLThkZmItNDAwYjZmZjNmN2JmIl0sInByaW1hcnlfb3JnX2lkIjoiNzE0YzdiOTktZjFkZC00ZWMxLThkZmItNDAwYjZmZjNmN2JmIiwicHJpbWFyeV9vcmdfcm9sZSI6ImFkbWluIiwib3JnX2luZm8iOlt7Im9yZ19pZCI6IjcxNGM3Yjk5LWYxZGQtNGVjMS04ZGZiLTQwMGI2ZmYzZjdiZiIsIm9yZ19uYW1lIjoiSW9USHViIiwicm9sZSI6ImFkbWluIiwiaXNfYWN0aXZlIjp0cnVlfV0sImV4cCI6MTc1NzUxNTk2N30.7afTU72PDHuC6bLHbtToLxYRiBeUEJh1n2vUlqCTqhs"

base_url = "http://localhost:8000"
headers = {"Authorization": f"Bearer {token}"}

def test_auth():
    print("🧪 Testing Authentication")
    print("=" * 40)
    
    try:
        # Test the correct endpoint
        response = requests.get(f"{base_url}/api/v1/users", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Success! Found {len(users)} users")
            for i, user in enumerate(users[:3]):  # Show first 3 users
                print(f"   User {i+1}: {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detail: {error_detail}")
            except:
                print(f"   Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_fresh_login():
    print(f"\n🔄 Testing Fresh Login")
    print("=" * 40)
    
    # Test login first
    login_data = {
        "email": "gibsonoluka7@gmail.com",  # Using your email from token
        "password": "admin123"  # You'll need to update this with correct password
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/login", json=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            new_token = login_result["token"]
            print(f"✅ Fresh login successful!")
            print(f"   New token: {new_token[:50]}...")
            
            # Test with new token
            new_headers = {"Authorization": f"Bearer {new_token}"}
            response = requests.get(f"{base_url}/api/v1/users", headers=new_headers)
            
            if response.status_code == 200:
                users = response.json()
                print(f"✅ API call with fresh token successful! Found {len(users)} users")
            else:
                print(f"❌ API call with fresh token failed: {response.status_code}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Login test error: {e}")

if __name__ == "__main__":
    test_auth()
    test_fresh_login()
    
    print(f"\n💡 Summary:")
    print("1. Use endpoint: /api/v1/users")
    print("2. Use header: Authorization: Bearer <token>")
    print("3. If still failing, try fresh login to get new token")
