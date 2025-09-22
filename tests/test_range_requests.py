#!/usr/bin/env python3
"""
Test script to demonstrate Range header functionality for firmware downloads.
This script shows various Range header patterns that your API now supports.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
FIRMWARE_ID = "your-firmware-id-here"  # Replace with actual firmware ID
FILE_TYPE = "bin"  # or "hex", "bootloader"

# You'll need to get an authentication token first
AUTH_TOKEN = "your-auth-token-here"  # Replace with actual token

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def test_range_requests():
    """Test various Range header scenarios."""
    
    url = f"{BASE_URL}/firmware/{FIRMWARE_ID}/download/{FILE_TYPE}"
    
    print("Testing Range Header Implementation")
    print("=" * 50)
    
    # Test 1: HEAD request to get file size
    print("\n1. Getting file metadata with HEAD request...")
    try:
        response = requests.head(url, headers=headers)
        if response.status_code == 200:
            file_size = int(response.headers.get('Content-Length', 0))
            print(f"   ✓ File size: {file_size} bytes")
            print(f"   ✓ Accept-Ranges: {response.headers.get('Accept-Ranges', 'none')}")
        else:
            print(f"   ✗ HEAD request failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ HEAD request error: {e}")
        return
    
    # Test 2: Full file download (no Range header)
    print("\n2. Full file download (no Range header)...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"   ✓ Status: {response.status_code} OK")
            print(f"   ✓ Content-Length: {len(response.content)} bytes")
        else:
            print(f"   ✗ Full download failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Full download error: {e}")
    
    # Test 3: Range request - first 1024 bytes
    print("\n3. Range request - first 1024 bytes...")
    range_headers = headers.copy()
    range_headers["Range"] = "bytes=0-1023"
    try:
        response = requests.get(url, headers=range_headers)
        if response.status_code == 206:
            print(f"   ✓ Status: {response.status_code} Partial Content")
            print(f"   ✓ Content-Length: {len(response.content)} bytes")
            print(f"   ✓ Content-Range: {response.headers.get('Content-Range')}")
        else:
            print(f"   ✗ Range request failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Range request error: {e}")
    
    # Test 4: Range request - last 512 bytes
    print("\n4. Range request - last 512 bytes...")
    range_headers = headers.copy()
    range_headers["Range"] = "bytes=-512"
    try:
        response = requests.get(url, headers=range_headers)
        if response.status_code == 206:
            print(f"   ✓ Status: {response.status_code} Partial Content")
            print(f"   ✓ Content-Length: {len(response.content)} bytes")
            print(f"   ✓ Content-Range: {response.headers.get('Content-Range')}")
        else:
            print(f"   ✗ Range request failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Range request error: {e}")
    
    # Test 5: Range request - from byte 1000 to end
    print("\n5. Range request - from byte 1000 to end...")
    range_headers = headers.copy()
    range_headers["Range"] = "bytes=1000-"
    try:
        response = requests.get(url, headers=range_headers)
        if response.status_code == 206:
            print(f"   ✓ Status: {response.status_code} Partial Content")
            print(f"   ✓ Content-Length: {len(response.content)} bytes")
            print(f"   ✓ Content-Range: {response.headers.get('Content-Range')}")
        else:
            print(f"   ✗ Range request failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Range request error: {e}")
    
    # Test 6: Invalid range request (should return 416)
    print("\n6. Invalid range request (should return 416)...")
    range_headers = headers.copy()
    range_headers["Range"] = f"bytes={file_size + 1000}-{file_size + 2000}"
    try:
        response = requests.get(url, headers=range_headers)
        if response.status_code == 416:
            print(f"   ✓ Status: {response.status_code} Range Not Satisfiable")
            print(f"   ✓ Content-Range: {response.headers.get('Content-Range')}")
        else:
            print(f"   ✗ Expected 416, got: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Invalid range test error: {e}")

def demonstrate_resume_download():
    """Demonstrate how to use Range headers for resuming downloads."""
    
    print("\n" + "=" * 50)
    print("Resume Download Demonstration")
    print("=" * 50)
    
    url = f"{BASE_URL}/firmware/{FIRMWARE_ID}/download/{FILE_TYPE}"
    
    # Simulate downloading first part
    print("\n1. Downloading first 2048 bytes...")
    range_headers = headers.copy()
    range_headers["Range"] = "bytes=0-2047"
    
    try:
        response = requests.get(url, headers=range_headers)
        if response.status_code == 206:
            first_part = response.content
            print(f"   ✓ Downloaded {len(first_part)} bytes")
            
            # Parse the Content-Range to get total file size
            content_range = response.headers.get('Content-Range')
            total_size = int(content_range.split('/')[-1])
            
            # Simulate resuming from where we left off
            print(f"\n2. Resuming download from byte 2048...")
            range_headers["Range"] = f"bytes=2048-"
            
            response = requests.get(url, headers=range_headers)
            if response.status_code == 206:
                second_part = response.content
                print(f"   ✓ Downloaded remaining {len(second_part)} bytes")
                
                # Verify total size
                total_downloaded = len(first_part) + len(second_part)
                print(f"   ✓ Total file size: {total_size} bytes")
                print(f"   ✓ Total downloaded: {total_downloaded} bytes")
                print(f"   ✓ Match: {'✓' if total_downloaded == total_size else '✗'}")
            else:
                print(f"   ✗ Resume failed: {response.status_code}")
        else:
            print(f"   ✗ Initial download failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Resume demo error: {e}")

if __name__ == "__main__":
    print("Range Header Test Script")
    print("=" * 50)
    print("\nBefore running this script:")
    print("1. Start your FastAPI server")
    print("2. Update FIRMWARE_ID with a valid firmware ID")
    print("3. Update AUTH_TOKEN with a valid authentication token")
    print("4. Ensure the firmware file exists in your cloud storage")
    
    # Uncomment the lines below after updating the configuration
    # test_range_requests()
    # demonstrate_resume_download()
    
    print("\nRange Header Features Implemented:")
    print("✓ HTTP 206 Partial Content responses")
    print("✓ HTTP 416 Range Not Satisfiable for invalid ranges")
    print("✓ Support for bytes=start-end format")
    print("✓ Support for bytes=start- format (from start to end)")
    print("✓ Support for bytes=-suffix format (last N bytes)")
    print("✓ Proper Content-Range and Content-Length headers")
    print("✓ Accept-Ranges: bytes header in all responses")
    print("✓ HEAD endpoint for getting file metadata")
