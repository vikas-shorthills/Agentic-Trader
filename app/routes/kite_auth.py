"""
Kite Connect Authentication Routes

Handles Kite Connect OAuth flow:
1. User clicks "Connect to Kite" -> redirects to Kite login
2. User authorizes -> Kite redirects back with request_token
3. Backend exchanges request_token for access_token
4. Access token is saved and used for trading
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from app.config.settings import settings

router = APIRouter(prefix="/auth/kite", tags=["kite-auth"])

# Configuration
# properly load from settings which handles .env file
API_KEY = settings.zerodha_api_key.strip() if settings.zerodha_api_key else None
API_SECRET = settings.zerodha_api_secret.strip() if settings.zerodha_api_secret else None
REDIRECT_URL = settings.zerodha_redirect_url or "http://localhost:7777/auth/kite/callback"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7777")

# In-memory storage with file persistence
SESSION_FILE = Path("/home/shtlp_0170/Videos/hackthon/Agentic-Trader/cache/kite_session.json")
kite_session = {
    "access_token": None,
    "user_id": None,
    "expires_at": None,
}


def load_session_from_file():
    """Load session from file on startup"""
    try:
        from pathlib import Path
        import json
        from app.services.scheduler_service import schedule_auto_logout
        
        if SESSION_FILE.exists():
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
                kite_session["access_token"] = data.get("access_token")
                kite_session["user_id"] = data.get("user_id")
                kite_session["expires_at"] = data.get("expires_at")
            
            # Check expiry and schedule logout
            if kite_session.get("expires_at"):
                try:
                    expires_at = datetime.fromisoformat(kite_session["expires_at"])
                    if datetime.now() < expires_at:
                        print(f"✅ Loaded persistent Kite session from {SESSION_FILE}")
                        schedule_auto_logout(expires_at)
                        return True
                    else:
                        print("⏳ Loaded session is expired. Clearing...")
                        kite_session["access_token"] = None
                        kite_session["user_id"] = None
                        kite_session["expires_at"] = None
                        save_session_to_file()
                except ValueError:
                    pass
                    
            print(f"✅ Loaded persistent Kite session (expired/invalid) from {SESSION_FILE}")
            return True
            
    except Exception as e:
        print(f"⚠️  Failed to load session from file: {e}")
    return False

# Attempt to load session on module import
load_session_from_file()


def save_session_to_file():
    """Save current session to file and schedule logout"""
    try:
        from pathlib import Path
        import json
        from app.services.scheduler_service import schedule_auto_logout
        
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(kite_session, f, indent=2)
        print(f"💾 Saved Kite session to {SESSION_FILE}")
        
        # Schedule auto-logout if we have an expiry
        if kite_session.get("expires_at"):
            try:
                expires_at = datetime.fromisoformat(kite_session["expires_at"])
                schedule_auto_logout(expires_at)
            except ValueError:
                pass
                
    except Exception as e:
        print(f"❌ Failed to save session to file: {e}")


class KiteSessionResponse(BaseModel):
    """Response model for Kite session info"""
    is_authenticated: bool
    user_id: Optional[str] = None
    expires_at: Optional[str] = None


class SaveTokenRequest(BaseModel):
    """Request model for saving access token"""
    access_token: str


class SaveTokenResponse(BaseModel):
    """Response model for saving access token"""
    success: bool
    user_id: Optional[str] = None
    expires_at: Optional[str] = None
    error: Optional[str] = None


@router.post("/save-token", response_model=SaveTokenResponse)
async def save_access_token(request: SaveTokenRequest):
    """
    Save access token received from frontend.
    The request_token from Kite callback IS the access token.
    
    Args:
        request: Contains the access_token from Kite callback
        
    Returns:
        SaveTokenResponse: Success status and session details
    """
    try:
        access_token = request.access_token
        
        # Store session data
        # Note: We don't have user_id from this flow, so we'll use a placeholder
        user_id = "KITE_USER"
        expires_at = (datetime.now() + timedelta(minutes=2)).isoformat()
        
        kite_session["access_token"] = access_token
        kite_session["user_id"] = user_id
        kite_session["expires_at"] = expires_at
        
        # Persist session to file
        save_session_to_file()
        
        # Update the access token in companies.py (legacy support)
        update_access_token_in_file(access_token)
        
        print(f"✅ Access token saved successfully: {access_token[:20]}...")
        
        return SaveTokenResponse(
            success=True,
            user_id=user_id,
            expires_at=expires_at
        )
            
    except Exception as e:
        print(f"❌ Error saving access token: {e}")
        return SaveTokenResponse(
            success=False,
            error=str(e)
        )


@router.get("/login")
async def kite_login():
    """
    Redirect user to Kite Connect login page.
    
    Returns:
        RedirectResponse: Redirects to Kite login URL
    """
    login_url = f"https://kite.zerodha.com/connect/login?api_key={API_KEY}&v=3"
    return RedirectResponse(url=login_url)


@router.get("/callback")
async def kite_callback(
    request_token: str = Query(..., description="Request token from Kite"),
    status: str = Query(default="success", description="Status from Kite")
):
    # Sanitize inputs
    request_token = request_token.strip() if request_token else request_token
    
    """
    Handle callback from Kite after user authorization.
    
    Args:
        request_token: The request token from Kite
        status: Status of the authentication
        
    Returns:
        RedirectResponse: Redirects to frontend with auth status
    """
    print(f"🔵 KITE CALLBACK RECEIVED: status={status}, token={request_token[:10]}...")
    
    if status != "success" or not request_token:
        print(f"🔴 Callback failed: status={status}, token_present={bool(request_token)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?kite_auth=failed&error=authorization_denied"
        )
    
    # Validate configuration
    if not API_KEY or not API_SECRET:
        print(f"🔴 Missing API Credentials: API_KEY={bool(API_KEY)}, API_SECRET={bool(API_SECRET)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?kite_auth=failed&error=server_configuration_error_missing_credentials"
        )
        
    print(f"🔵 Auth Debug: API_KEY_LEN={len(API_KEY)}, API_SECRET_LEN={len(API_SECRET)}")
    print(f"🔵 Auth Debug: API_KEY={API_KEY[:4]}...{API_KEY[-4:]}, API_SECRET={API_SECRET[:4]}...{API_SECRET[-4:]}")
    
    try:
        # Generate session using request token
        import requests
        
        # Generate checksum: sha256(api_key + request_token + api_secret)
        checksum_string = API_KEY + request_token + API_SECRET
        checksum = hashlib.sha256(checksum_string.encode()).hexdigest()
        
        # Make API call to generate session
        url = "https://api.kite.trade/session/token"
        payload = {
            "api_key": API_KEY,
            "request_token": request_token,
            "checksum": checksum
        }
        
        print(f"🔵 Requesting session from Kite API: {url}")
        response = requests.post(url, data=payload)
        
        if not response.ok:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {'message': response.text}
            error_msg = error_data.get('message', 'Unknown Error')
            print(f"🔴 Kite API Error: {error_msg}")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?kite_auth=failed&error={error_msg}"
            )
            
        response.raise_for_status()
        data = response.json()
        print(f"🟢 Kite API Response: {data.get('status')}")
        
        if data.get('status') == 'success':
            # Store session data
            kite_session["access_token"] = data['data']['access_token']
            kite_session["user_id"] = data['data']['user_id']
            kite_session["expires_at"] = (datetime.now() + timedelta(hours=4)).isoformat()
            
            # Persist session to file
            print("🔵 Attempting to save session to file...")
            save_session_to_file()
            
            # Update the access token in companies.py
            update_access_token_in_file(data['data']['access_token'])
            
            print(f"🟢 Callback processed successfully. Redirecting to frontend: {FRONTEND_URL}")
            # Redirect to frontend with success
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?kite_auth=success&user_id={data['data']['user_id']}"
            )
        else:
            print(f"🔴 Kite API status not success: {data}")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?kite_auth=failed&error=session_generation_failed"
            )
            
    except Exception as e:
        print(f"❌ Error in Kite callback: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?kite_auth=failed&error={str(e)}"
        )


@router.get("/status", response_model=KiteSessionResponse)
async def get_kite_status():
    """
    Get current Kite authentication status.
    
    Returns:
        KiteSessionResponse: Current authentication status
    """
    # Try to load if not in memory (redundancy)
    if not kite_session.get("access_token"):
        load_session_from_file()
        
    is_authenticated = False
    
    if kite_session.get("access_token") and kite_session.get("expires_at"):
        # Check if token is still valid
        expires_at = datetime.fromisoformat(kite_session["expires_at"])
        is_authenticated = datetime.now() < expires_at
    
    return KiteSessionResponse(
        is_authenticated=is_authenticated,
        user_id=kite_session.get("user_id"),
        expires_at=kite_session.get("expires_at")
    )


@router.post("/logout")
async def kite_logout():
    """
    Logout from Kite (clear session).
    
    Returns:
        dict: Success message
    """
    kite_session["access_token"] = None
    kite_session["user_id"] = None
    kite_session["expires_at"] = None
    
    # Update file to clear session
    save_session_to_file()
    
    return {"success": True, "message": "Logged out successfully"}


def update_access_token_in_file(access_token: str):
    """
    Update the ACCESS_TOKEN in .env file.
    
    Args:
        access_token: New access token to save
    """
    try:
        env_file = "/home/shtlp_0170/Videos/hackthon/Agentic-Trader/.env"
        
        # Read the file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update the ZERODHA_ACCESS_TOKEN line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('ZERODHA_ACCESS_TOKEN='):
                lines[i] = f'ZERODHA_ACCESS_TOKEN={access_token}\n'
                updated = True
                break
        
        # If not found, append it
        if not updated:
            lines.append(f'ZERODHA_ACCESS_TOKEN={access_token}\n')
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Updated ZERODHA_ACCESS_TOKEN in .env file")
        
    except Exception as e:
        print(f"⚠️  Failed to update ZERODHA_ACCESS_TOKEN in .env: {e}")


def get_current_access_token() -> Optional[str]:
    """
    Get current access token.
    
    Returns:
        str: Current access token or None
    """
    # Ensure loaded
    if not kite_session.get("access_token"):
        load_session_from_file()
        
    return kite_session.get("access_token")
