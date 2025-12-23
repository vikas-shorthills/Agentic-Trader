
import os
import hashlib
from app.config.settings import settings

def verify():
    print("--- Credential Verification Script ---")
    
    # Reload settings to ensure fresh load
    api_key = settings.zerodha_api_key
    api_secret = settings.zerodha_api_secret
    
    print(f"Loaded from settings module:")
    print(f"API_KEY: '{api_key}' (Len: {len(api_key) if api_key else 0})")
    print(f"API_SECRET: '{api_secret}' (Len: {len(api_secret) if api_secret else 0})")
    
    if not api_key or not api_secret:
        print("❌ Credentials missing in settings!")
        return

    # Check for whitespace
    if api_key != api_key.strip():
        print("⚠️  API_KEY has leading/trailing whitespace!")
    if api_secret != api_secret.strip():
        print("⚠️  API_SECRET has leading/trailing whitespace!")

    # Test Checksum Calculation
    print("\n--- Test Checksum Calculation ---")
    request_token = "test_token_123"
    checksum_string = api_key.strip() + request_token + api_secret.strip()
    checksum = hashlib.sha256(checksum_string.encode()).hexdigest()
    
    print(f"Test Input: API_KEY + '{request_token}' + API_SECRET")
    print(f"Calculated Checksum: {checksum}")
    print("--------------------------------------")

if __name__ == "__main__":
    verify()
