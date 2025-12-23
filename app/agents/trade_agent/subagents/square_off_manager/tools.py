"""Square-Off Manager Tools"""

from typing import Dict
from datetime import datetime
from app.services.zerodha_service import get_zerodha_service


def get_open_positions() -> Dict:
    """
    Get all open intraday positions.
    
    Returns:
        Dict with open positions
    """
    try:
        zerodha = get_zerodha_service()
        positions = zerodha.get_positions()
        day_positions = positions.get("day", [])
        
        open_positions = []
        total_pnl = 0
        
        for pos in day_positions:
            qty = pos.get("quantity", 0)
            if qty != 0:
                pnl = pos.get("pnl", 0)
                total_pnl += pnl
                open_positions.append({
                    "symbol": pos.get("tradingsymbol"),
                    "quantity": qty,
                    "average_price": pos.get("average_price"),
                    "last_price": pos.get("last_price"),
                    "pnl": pnl,
                    "product": pos.get("product"),
                    "exchange": pos.get("exchange"),
                })
        
        return {
            "open_positions": open_positions,
            "count": len(open_positions),
            "total_unrealized_pnl": total_pnl,
        }
    except Exception as e:
        return {"error": str(e)}


def close_position(symbol: str, exchange: str = "NSE") -> Dict:
    """
    Close an open position by placing opposite order.
    
    Args:
        symbol: Stock symbol
        exchange: Exchange
        
    Returns:
        Dict with close order details
    """
    try:
        zerodha = get_zerodha_service()
        positions = zerodha.get_positions()
        day_positions = positions.get("day", [])
        
        # Find the position
        position = None
        for pos in day_positions:
            if pos.get("tradingsymbol") == symbol and pos.get("quantity", 0) != 0:
                position = pos
                break
        
        if not position:
            return {"error": f"No open position found for {symbol}"}
        
        quantity = abs(position.get("quantity", 0))
        transaction_type = "SELL" if position.get("quantity", 0) > 0 else "BUY"
        
        # Place closing order
        order_id = zerodha.place_order(
            tradingsymbol=symbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            order_type="MARKET",
            product=position.get("product", "MIS"),
            tag="SQUARE_OFF"
        )
        
        return {
            "order_id": order_id,
            "symbol": symbol,
            "closed_quantity": quantity,
            "transaction_type": transaction_type,
            "position_pnl": position.get("pnl", 0),
            "status": "CLOSED"
        }
    except Exception as e:
        return {"error": str(e)}


def get_trading_hours_status() -> Dict:
    """
    Check if market is open and time until close.
    
    Returns:
        Dict with market status
    """
    now = datetime.now()
    
    # Market hours (IST)
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    square_off_time = now.replace(hour=15, minute=10, second=0, microsecond=0)
    
    is_market_open = market_open <= now <= market_close
    is_weekday = now.weekday() < 5
    
    minutes_to_close = int((market_close - now).total_seconds() / 60) if is_market_open else 0
    should_square_off = now >= square_off_time if is_market_open else False
    
    return {
        "current_time": now.strftime("%H:%M:%S"),
        "is_trading_day": is_weekday,
        "is_market_open": is_market_open and is_weekday,
        "minutes_to_close": minutes_to_close,
        "should_square_off": should_square_off,
    }
