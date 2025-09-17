#!/usr/bin/env python3
"""
Test script to verify the updated selfconfig endpoint with new URL structure
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_selfconfig_endpoint():
    """Test the new selfconfig endpoint structure"""
    
    # Test parameters
    org_token = "McAzb5kazwe92ToKkmcV_A"
    network_id = "8944501905220512557"
    
    url = f"{BASE_URL}/network/selfconfig"
    
    print(f"Testing new endpoint: {url}")
    
    # Test 1: Request without query parameters (should fail)
    print("\n1️⃣ Testing without query parameters...")
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Request with only org_token (should fail - missing networkID)
    print("\n2️⃣ Testing with only org_token...")
    try:
        response = requests.get(url, params={"org_token": org_token})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Request with both required parameters (should work)
    print("\n3️⃣ Testing with both org_token and networkID...")
    try:
        response = requests.get(url, params={
            "org_token": org_token,
            "networkID": network_id
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing updated selfconfig endpoint structure...")
    test_selfconfig_endpoint()