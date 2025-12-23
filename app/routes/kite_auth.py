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

router = APIRouter(prefix="/auth/kite", tags=["kite-auth"])

# Configuration - These should be in environment variables
API_KEY = os.getenv("ZERODHA_API_KEY")
API_SECRET = os.getenv("ZERODHA_API_SECRET")
REDIRECT_URL = os.getenv("ZERODHA_REDIRECT_URL", "http://localhost:7777/auth/kite/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:7777")

# In-memory storage (in production, use Redis or database)
kite_session = {
    "access_token": None,
    "user_id": None,
    "expires_at": None,
}


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
        user_id = "KITE_USER"  # You can fetch this later using the access token if needed
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        kite_session["access_token"] = access_token
        kite_session["user_id"] = user_id
        kite_session["expires_at"] = expires_at
        
        # Update the access token in companies.py
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
    """
    Handle callback from Kite after user authorization.
    
    Args:
        request_token: The request token from Kite
        status: Status of the authentication
        
    Returns:
        RedirectResponse: Redirects to frontend with auth status
    """
    if status != "success" or not request_token:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?kite_auth=failed&error=authorization_denied"
        )
    
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
        
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            # Store session data
            kite_session["access_token"] = data['data']['access_token']
            kite_session["user_id"] = data['data']['user_id']
            kite_session["expires_at"] = (datetime.now() + timedelta(hours=24)).isoformat()
            
            # Update the access token in companies.py
            update_access_token_in_file(data['data']['access_token'])
            
            # Redirect to frontend with success
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?kite_auth=success&user_id={data['data']['user_id']}"
            )
        else:
            return RedirectResponse(
                url=f"{FRONTEND_URL}/?kite_auth=failed&error=session_generation_failed"
            )
            
    except Exception as e:
        print(f"Error in Kite callback: {e}")
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
    return kite_session.get("access_token")
