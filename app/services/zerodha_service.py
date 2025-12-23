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
        
        # Initialize KiteConnect
        self.kite = None
        if self.api_key:
            self.kite = KiteConnect(api_key=self.api_key)
            if self.access_token:
                self.kite.set_access_token(self.access_token)
        else:
            print("WARNING: zerodha_api_key not found. ZerodhaService will not be fully functional.")
    
    def _ensure_authenticated(self) -> KiteConnect:
        """Internal helper to ensure KiteConnect is ready for API calls."""
        if not self.kite:
            raise ValueError("KiteConnect not initialized. Please provide ZERODHA_API_KEY.")
        if not self.access_token:
            raise ValueError("Authentication required. Please log in to Zerodha via the login flow.")
        return self.kite
    
    def get_login_url(self) -> str:
        """
        Get login URL for manual authentication
        
        Returns:
            Login URL string
        """
        return self._ensure_kite().login_url()
    
    def generate_session(self, request_token: str) -> dict:
        """
        Generate session and get access token
        
        Args:
            request_token: Token obtained after user login
            
        Returns:
            Session data dict with access_token
        """
        if not self.api_secret:
            raise ValueError("zerodha_api_secret missing. Cannot generate session.")
            
        kite = self._ensure_kite()
        data = kite.generate_session(request_token, api_secret=self.api_secret)
        kite.set_access_token(data["access_token"])
        self.access_token = data["access_token"]  # Update local state too
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
    
    # =========================================================================
    # ORDER MANAGEMENT
    # =========================================================================
    
    def place_order(
        self,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        order_type: str = "MARKET",
        product: str = "MIS",
        price: float = None,
        trigger_price: float = None,
        validity: str = "DAY",
        tag: str = None
    ) -> str:
        """
        Place an order on Zerodha
        
        Args:
            tradingsymbol: Trading symbol (e.g., 'RELIANCE', 'INFY')
            exchange: Exchange (NSE, BSE, NFO, MCX)
            transaction_type: BUY or SELL
            quantity: Number of shares/lots
            order_type: MARKET, LIMIT, SL, SL-M
            product: MIS (intraday), CNC (delivery), NRML (F&O)
            price: Limit price (required for LIMIT orders)
            trigger_price: Trigger price (required for SL orders)
            validity: DAY or IOC
            tag: Optional tag for order identification
            
        Returns:
            Order ID string
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        
        order_params = {
            "tradingsymbol": tradingsymbol,
            "exchange": exchange,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "order_type": order_type,
            "product": product,
            "validity": validity,
        }
        
        if price is not None:
            order_params["price"] = price
        if trigger_price is not None:
            order_params["trigger_price"] = trigger_price
        if tag is not None:
            order_params["tag"] = tag
            
        return self.kite.place_order(variety="regular", **order_params)
    
    def place_sl_order(
        self,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        trigger_price: float,
        price: float = None,
        product: str = "MIS",
        tag: str = None
    ) -> str:
        """
        Place a stop-loss order
        
        Args:
            tradingsymbol: Trading symbol
            exchange: Exchange
            transaction_type: BUY or SELL
            quantity: Number of shares/lots
            trigger_price: Stop-loss trigger price
            price: Limit price (if None, uses SL-M market order)
            product: MIS (intraday), CNC (delivery), NRML (F&O)
            tag: Optional tag
            
        Returns:
            Order ID string
        """
        order_type = "SL" if price is not None else "SL-M"
        return self.place_order(
            tradingsymbol=tradingsymbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            order_type=order_type,
            product=product,
            price=price,
            trigger_price=trigger_price,
            tag=tag
        )
    
    def modify_order(
        self,
        order_id: str,
        quantity: int = None,
        price: float = None,
        trigger_price: float = None,
        order_type: str = None
    ) -> str:
        """
        Modify a pending order
        
        Args:
            order_id: Order ID to modify
            quantity: New quantity (optional)
            price: New price (optional)
            trigger_price: New trigger price (optional)
            order_type: New order type (optional)
            
        Returns:
            Order ID string
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        
        modify_params = {"order_id": order_id}
        if quantity is not None:
            modify_params["quantity"] = quantity
        if price is not None:
            modify_params["price"] = price
        if trigger_price is not None:
            modify_params["trigger_price"] = trigger_price
        if order_type is not None:
            modify_params["order_type"] = order_type
            
        return self.kite.modify_order(variety="regular", **modify_params)
    
    def cancel_order(self, order_id: str) -> str:
        """
        Cancel a pending order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Order ID string
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.cancel_order(variety="regular", order_id=order_id)
    
    def get_orders(self) -> list:
        """
        Get list of all orders for the day
        
        Returns:
            List of order dicts
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.orders()
    
    def get_order_history(self, order_id: str) -> list:
        """
        Get history of a specific order
        
        Args:
            order_id: Order ID
            
        Returns:
            List of order status updates
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.order_history(order_id)
    
    # =========================================================================
    # PORTFOLIO MANAGEMENT
    # =========================================================================
    
    def get_positions(self) -> dict:
        """
        Get current positions (day and net)
        
        Returns:
            Dict with 'day' and 'net' position lists
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.positions()
    
    def get_holdings(self) -> list:
        """
        Get holdings (delivery stocks)
        
        Returns:
            List of holding dicts
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.holdings()
    
    def get_margins(self, segment: str = None) -> dict:
        """
        Get account margins
        
        Args:
            segment: Optional segment filter ('equity', 'commodity')
            
        Returns:
            Dict with margin details
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        if segment:
            return self.kite.margins(segment)
        return self.kite.margins()
    
    def get_available_margin(self) -> float:
        """
        Get total available margin for trading
        
        Returns:
            Available margin as float
        """
        margins = self.get_margins()
        equity_margin = margins.get("equity", {})
        available = equity_margin.get("available", {})
        return available.get("live_balance", 0) + available.get("adhoc_margin", 0)
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_ltp(self, instruments: list) -> dict:
        """
        Get Last Traded Price for instruments
        
        Args:
            instruments: List of instrument keys (e.g., ['NSE:INFY'])
            
        Returns:
            Dict with LTP data
        """
        if not self.access_token:
            raise ValueError("Access token not set. Please authenticate first.")
        return self.kite.ltp(instruments)
    
    def search_instruments(
        self,
        query: str,
        exchange: str = "NSE"
    ) -> list:
        """
        Search for instruments by name
        
        Args:
            query: Search query (e.g., 'RELIANCE')
            exchange: Exchange to search in
            
        Returns:
            List of matching instruments
        """
        instruments = self.get_instruments(exchange)
        query_upper = query.upper()
        return [
            inst for inst in instruments
            if query_upper in inst.get("tradingsymbol", "").upper()
            or query_upper in inst.get("name", "").upper()
        ]
    
    def get_instrument_token(
        self,
        tradingsymbol: str,
        exchange: str = "NSE"
    ) -> int:
        """
        Get instrument token for a trading symbol
        
        Args:
            tradingsymbol: Trading symbol (e.g., 'RELIANCE')
            exchange: Exchange
            
        Returns:
            Instrument token (int)
        """
        instruments = self.get_instruments(exchange)
        for inst in instruments:
            if inst.get("tradingsymbol") == tradingsymbol:
                return inst.get("instrument_token")
        raise ValueError(f"Instrument {tradingsymbol} not found on {exchange}")


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

