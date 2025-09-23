#!/usr/bin/env python3
"""
Test script to verify Google Cloud credentials are working properly.
Run this script to check if your GCP setup is correct before deploying.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from utils.gcp_utils import load_gcp_credentials
from dotenv import load_dotenv

def test_credentials():
    """Test that GCP credentials can be loaded and used."""
    
    print("🔍 Testing Google Cloud Platform Credentials")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test credential loading
    print("1. Testing credential loading...")
    credentials = load_gcp_credentials()
    
    if credentials is None:
        print("❌ FAILED: No credentials could be loaded!")
        print("\n🔧 Please check:")
        print("   - service-account.json exists in project root")
        print("   - GOOGLE_APPLICATION_CREDENTIALS points to valid file")  
        print("   - GOOGLE_APPLICATION_CREDENTIALS_JSON contains valid JSON")
        return False
    
    print("✅ SUCCESS: Credentials loaded successfully!")
    print(f"   Service account email: {credentials.service_account_email}")
    
    # Test Google Cloud Storage client
    print("\n2. Testing Google Cloud Storage client...")
    try:
        from google.cloud import storage
        client = storage.Client(credentials=credentials)
        
        # Get bucket name
        bucket_name = os.getenv("BUCKET_NAME")
        if not bucket_name:
            print("⚠️  WARNING: BUCKET_NAME not set in environment variables")
            return True  # Credentials work, but bucket not configured
        
        print(f"   Bucket name: {bucket_name}")
        
        # Test bucket access (this will make an actual API call)
        bucket = client.bucket(bucket_name)
        exists = bucket.exists()
        
        if exists:
            print("✅ SUCCESS: Can access Google Cloud Storage bucket!")
            
            # Try to list some blobs (optional)
            try:
                blobs = list(client.list_blobs(bucket_name, max_results=1))
                print(f"   Found {len(blobs)} blob(s) in bucket")
            except Exception as e:
                print(f"   Note: Could not list blobs: {e}")
        else:
            print(f"❌ FAILED: Bucket '{bucket_name}' does not exist or is not accessible")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error testing storage client: {e}")
        return False
    
    return True

def check_environment():
    """Check environment configuration."""
    
    print("\n🔧 Environment Configuration Check")
    print("=" * 50)
    
    # Check for credentials file
    creds_file = Path("service-account.json")
    if creds_file.exists():
        print("✅ service-account.json found")
    else:
        print("❌ service-account.json not found")
    
    # Check environment variables
    env_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_APPLICATION_CREDENTIALS_JSON", 
        "BUCKET_NAME",
        "DATABASE_URL"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == "GOOGLE_APPLICATION_CREDENTIALS_JSON":
                print(f"✅ {var}: Set ({len(value)} characters)")
            elif var == "DATABASE_URL":
                # Hide sensitive parts of DB URL
                if "postgresql://" in value:
                    print(f"✅ {var}: Set (PostgreSQL)")
                else:
                    print(f"✅ {var}: Set")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")

def main():
    """Main test function."""
    
    print("🚀 GCP Credentials Test Suite")
    print("=" * 50)
    
    # Check environment first
    check_environment()
    
    # Test credentials
    success = test_credentials()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Your GCP credentials are properly configured!")
        print("\n💡 You can now:")
        print("   - Deploy your FastAPI service")
        print("   - Upload/download firmware files")
        print("   - Use Google Cloud Storage features")
    else:
        print("❌ FAILED: GCP credentials need to be fixed")
        print("\n🔧 Next steps:")
        print("   1. Ensure service-account.json exists and is valid")
        print("   2. Check your .env file configuration") 
        print("   3. Verify your Google Cloud project settings")
        print("   4. Make sure the service account has proper permissions")

if __name__ == "__main__":
    main()