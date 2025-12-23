"""
Universe Scanner Tools

Tools for validating stocks and checking market data.
"""

from typing import Dict
import numpy as np
from app.services.zerodha_service import get_zerodha_service


def get_stock_quote(symbol: str, exchange: str = "NSE") -> Dict:
    """
    Get current quote for a stock including LTP, OHLC, and volume.
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE')
        exchange: Exchange (default: 'NSE')
        
    Returns:
        Dict with quote data including last_price, ohlc, volume
    """
    try:
        zerodha = get_zerodha_service()
        instrument_key = f"{exchange}:{symbol}"
        quote = zerodha.get_quote([instrument_key])
        
        if instrument_key in quote:
            data = quote[instrument_key]
            return {
                "symbol": symbol,
                "exchange": exchange,
                "last_price": data.get("last_price"),
                "open": data.get("ohlc", {}).get("open"),
                "high": data.get("ohlc", {}).get("high"),
                "low": data.get("ohlc", {}).get("low"),
                "close": data.get("ohlc", {}).get("close"),
                "volume": data.get("volume"),
                "buy_quantity": data.get("buy_quantity"),
                "sell_quantity": data.get("sell_quantity"),
                "average_price": data.get("average_price"),
                "last_trade_time": str(data.get("last_trade_time")),
            }
        return {"error": f"Quote not found for {instrument_key}"}
    except Exception as e:
        return {"error": str(e)}


def get_volume_analysis(symbol: str, exchange: str = "NSE") -> Dict:
    """
    Analyze current volume relative to average.
    
    Args:
        symbol: Stock symbol
        exchange: Exchange
        
    Returns:
        Dict with volume metrics
    """
    try:
        zerodha = get_zerodha_service()
        from datetime import datetime, timedelta
        
        # Get instrument token
        instrument_token = zerodha.get_instrument_token(symbol, exchange)
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        # Fetch daily candles
        candles = zerodha.get_historical_data(
            instrument_token=instrument_token,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
            interval="day"
        )
        
        if not candles or len(candles) < 20:
            return {"error": "Not enough volume history"}
        
        volumes = [c["volume"] for c in candles]
        avg_volume = np.mean(volumes[-20:])  # 20-day average
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Determine quality
        if volume_ratio > 2.0:
            quality = "HIGH"
        elif volume_ratio > 1.0:
            quality = "NORMAL"
        else:
            quality = "LOW"
        
        return {
            "symbol": symbol,
            "current_volume": current_volume,
            "average_volume_20d": avg_volume,
            "volume_ratio": round(volume_ratio, 2),
            "volume_quality": quality,
            "interpretation": f"Current volume is {volume_ratio:.1f}x the 20-day average"
        }
    except Exception as e:
        return {"error": str(e)}
