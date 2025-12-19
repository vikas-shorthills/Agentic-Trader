"""
Zerodha Kite Connect Service
Simple service for Zerodha API authentication and operations
"""
import os
from pathlib import Path
from kiteconnect import KiteConnect
from app.config.settings import settings


class ZerodhaService:
    """
    Service for Zerodha Kite Connect API
    Handles authentication and API calls
    """
    
    def __init__(self):
        """Initialize Zerodha service with credentials from environment"""
        self.api_key = settings.zerodha_api_key
        self.api_secret = settings.zerodha_api_secret
        self.access_token = settings.zerodha_access_token
        self.redirect_url = settings.zerodha_redirect_url
        
        if not self.api_key:
            raise ValueError("zerodha_api_key not found in environment variables")
        
        if not self.api_secret:
            raise ValueError("zerodha_api_secret not found in environment variables")
        
        # Initialize KiteConnect
        self.kite = KiteConnect(api_key=self.api_key)
        
        # Set access token if available
        if self.access_token:
            self.kite.set_access_token(self.access_token)
    
    def get_login_url(self) -> str:
        """
        Get login URL for manual authentication
        
        Returns:
            Login URL string
        """
        return self.kite.login_url()
    
    def generate_session(self, request_token: str) -> dict:
        """
        Generate session and get access token
        
        Args:
            request_token: Token obtained after user login
            
        Returns:
            Session data dict with access_token
            
        Example:
            data = service.generate_session("your_request_token")
            access_token = data["access_token"]
        """
        data = self.kite.generate_session(request_token, api_secret=self.api_secret)
        self.kite.set_access_token(data["access_token"])
        return data
    
    def get_instruments(self, exchange: str = "NSE") -> list:
        """
        Get list of instruments for an exchange
        
        Args:
            exchange: Exchange name (NSE, BSE, NFO, etc.)
            
        Returns:
            List of instruments
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.instruments(exchange)
    
    def get_quote(self, instruments: list) -> dict:
        """
        Get market quotes for instruments
        
        Args:
            instruments: List of instrument keys (e.g., ['NSE:INFY', 'NSE:TCS'])
            
        Returns:
            Dict with quote data
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.quote(instruments)
    
    def get_ohlc(self, instruments: list) -> dict:
        """
        Get OHLC data for instruments
        
        Args:
            instruments: List of instrument keys
            
        Returns:
            Dict with OHLC data
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.ohlc(instruments)
    
    def get_historical_data(
        self,
        instrument_token: str,
        from_date: str,
        to_date: str,
        interval: str = "day"
    ) -> list:
        """
        Get historical candle data
        
        Args:
            instrument_token: Instrument token
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            interval: Candle interval (minute, day, etc.)
            
        Returns:
            List of OHLC candles
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.historical_data(
            instrument_token,
            from_date,
            to_date,
            interval
        )


# Singleton instance
_zerodha_service = None


def get_zerodha_service() -> ZerodhaService:
    """
    Get singleton Zerodha service instance
    
    Returns:
        ZerodhaService instance
    """
    global _zerodha_service
    if _zerodha_service is None:
        _zerodha_service = ZerodhaService()
    return _zerodha_service

