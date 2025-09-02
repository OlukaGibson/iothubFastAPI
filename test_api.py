#!/usr/bin/env python3
"""
Simple test script to check if the API endpoints are working
"""
import requests
import json
import time

def test_device_endpoint():
    """Test the device endpoint that was causing the error"""
    try:
        print("Testing GET /api/v1/device endpoint...")
        response = requests.get('http://localhost:8000/api/v1/device', timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! No more database connection errors.")
            print(f"Response: {response.json()}")
        elif response.status_code == 401:
            print("✅ Success! Authentication is working (401 Unauthorized is expected without proper auth).")
            print(f"Response: {response.json()}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure server is running on localhost:8000")
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        print("\nTesting GET / endpoint...")
        response = requests.get('http://localhost:8000/', timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_root_endpoint()
    test_device_endpoint()
