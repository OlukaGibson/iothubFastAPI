#!/usr/bin/env python3
"""
Test with debug output to see exactly what's happening with the token.
"""

import requests
import json

# Your JWT token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjRlMzJjZmItYWY3My00ZTNiLWJjODItZmVkNTdlODE5NmRlIiwiZW1haWwiOiJnaWJzb25vbHVrYTdAZ21haWwuY29tIiwiaXNfYWRtaW4iOnRydWUsIm9yZ19pZHMiOlsiNzE0YzdiOTktZjFkZC00ZWMxLThkZmItNDAwYjZmZjNmN2JmIl0sInByaW1hcnlfb3JnX2lkIjoiNzE0YzdiOTktZjFkZC00ZWMxLThkZmItNDAwYjZmZjNmN2JmIiwicHJpbWFyeV9vcmdfcm9sZSI6ImFkbWluIiwib3JnX2luZm8iOlt7Im9yZ19pZCI6IjcxNGM3Yjk5LWYxZGQtNGVjMS04ZGZiLTQwMGI2ZmYzZjdiZiIsIm9yZ19uYW1lIjoiSW9USHViIiwicm9sZSI6ImFkbWluIiwiaXNfYWN0aXZlIjp0cnVlfV0sImV4cCI6MTc1NzUxNTk2N30.7afTU72PDHuC6bLHbtToLxYRiBeUEJh1n2vUlqCTqhs"

base_url = "http://localhost:8000"

def test_different_header_formats():
    print("🧪 Testing Different Authorization Header Formats")
    print("=" * 60)
    
    test_cases = [
        ("No header", {}),
        ("Bearer token", {"Authorization": f"Bearer {token}"}),
        ("bearer token (lowercase)", {"authorization": f"bearer {token}"}),
        ("Just token (no Bearer)", {"Authorization": token}),
        ("Wrong format", {"Authorization": f"Token {token}"}),
    ]
    
    for test_name, headers in test_cases:
        print(f"\n📋 Test: {test_name}")
        print(f"   Headers: {headers}")
        
        try:
            response = requests.get(f"{base_url}/api/v1/users", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
            else:
                users = response.json()
                print(f"   ✅ Success! Found {len(users)} users")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Could not connect to server")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_with_curl_format():
    print(f"\n🌐 cURL Command for Testing:")
    print("=" * 60)
    
    curl_command = f'''curl -X GET "{base_url}/api/v1/users" \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json"'''
    
    print(curl_command)
    
    print(f"\n📝 For Swagger/Postman:")
    print("Header Name: Authorization")
    print(f"Header Value: Bearer {token}")

if __name__ == "__main__":
    test_different_header_formats()
    test_with_curl_format()
    
    print(f"\n👀 Check your server console for DEBUG messages!")
    print("Look for lines starting with 🔍, 🔑, ✅, or ❌")
