"""
Google Cloud Platform credentials utilities.
Handles loading credentials from both file and JSON environment variables.
"""

import os
import json
from pathlib import Path
from google.oauth2 import service_account
from typing import Optional


def load_gcp_credentials() -> Optional[service_account.Credentials]:
    """
    Load GCP credentials using multiple methods in order of preference:
    1. GOOGLE_APPLICATION_CREDENTIALS environment variable (file path)
    2. service-account.json file in project root
    3. GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable (JSON string)
    
    Returns:
        service_account.Credentials object or None if no credentials found
    """
    
    # Method 1: Standard GOOGLE_APPLICATION_CREDENTIALS file path
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_file:
        credentials_path = Path(credentials_file)
        if credentials_path.exists():
            try:
                return service_account.Credentials.from_service_account_file(str(credentials_path))
            except Exception as e:
                print(f"Warning: Failed to load credentials from {credentials_file}: {e}")
    
    # Method 2: Default service-account.json in project root
    default_creds_path = Path("service-account.json")
    if default_creds_path.exists():
        try:
            return service_account.Credentials.from_service_account_file(str(default_creds_path))
        except Exception as e:
            print(f"Warning: Failed to load credentials from {default_creds_path}: {e}")
    
    # Method 3: Fallback to JSON string in environment variable
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if credentials_json:
        try:
            credentials_dict = json.loads(credentials_json)
            return service_account.Credentials.from_service_account_info(credentials_dict)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to load credentials from JSON env var: {e}")
    
    # No credentials found
    return None


def get_gcp_credentials_with_fallback() -> Optional[service_account.Credentials]:
    """
    Get GCP credentials with comprehensive error handling and fallbacks.
    
    Returns:
        service_account.Credentials object or None if no valid credentials found
    """
    return load_gcp_credentials()