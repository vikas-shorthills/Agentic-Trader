from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.services.zerodha_service import get_zerodha_service, ZerodhaService
from app.config.settings import settings
from app.loggers.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/zerodha/login")
async def zerodha_login(service: ZerodhaService = Depends(get_zerodha_service)):
    """
    Redirects the user to Zerodha's login page.
    """
    try:
        login_url = service.get_login_url()
        return {"login_url": login_url}
    except Exception as e:
        logger.error(f"Error getting Zerodha login URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not generate Zerodha login URL")

@router.get("/zerodha/callback")
async def zerodha_callback(request: Request, request_token: str = None, service: ZerodhaService = Depends(get_zerodha_service)):
    """
    Handles the request token from Zerodha and generates a session.
    """
    if not request_token:
        raise HTTPException(status_code=400, detail="request_token is required")
    
    try:
        session_data = service.generate_session(request_token)
        # In a real app, you would save this to a persistent session store
        # For now, we return it or set it in a cookie/session
        return {
            "status": "success",
            "message": "Authenticated successfully",
            "user_id": session_data.get("user_id"),
            "access_token": session_data.get("access_token")
        }
    except Exception as e:
        logger.error(f"Error generating Zerodha session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.get("/zerodha/session")
async def get_session(service: ZerodhaService = Depends(get_zerodha_service)):
    """
    Checks if there is an active Zerodha session.
    """
    if not service.access_token:
        return {"authenticated": False}
    
    try:
        # You might want to verify the token by making a small API call
        # e.g., service.kite.profile()
        return {
            "authenticated": True,
            "access_token": service.access_token
        }
    except Exception:
        return {"authenticated": False}
