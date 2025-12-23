"""Trend Agent Tools"""

from typing import Dict
from datetime import datetime, timedelta
import numpy as np

from app.services.zerodha_service import get_zerodha_service
from app.services.market_data.indicators import TechnicalIndicators


def get_historical_candles(
    symbol: str,
    interval: str = "15minute",
    days: int = 5,
    exchange: str = "NSE"
) -> Dict:
    """
    Get historical OHLCV candles for trend analysis.
    
    Args:
        symbol: Stock symbol
        interval: Candle interval ('15minute', 'hour', 'day')
        days: Number of days of history
        exchange: Exchange
        
    Returns:
        Dict with candle data arrays
    """
    try:
        zerodha = get_zerodha_service()
        instrument_token = zerodha.get_instrument_token(symbol, exchange)
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        candles = zerodha.get_historical_data(
            instrument_token=instrument_token,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
            interval=interval
        )
        
        if not candles:
            return {"error": "No candle data returned"}
        
        return {
            "symbol": symbol,
            "interval": interval,
            "candle_count": len(candles),
            "open": [c["open"] for c in candles],
            "high": [c["high"] for c in candles],
            "low": [c["low"] for c in candles],
            "close": [c["close"] for c in candles],
            "volume": [c["volume"] for c in candles],
            "latest_close": candles[-1]["close"] if candles else None,
        }
    except Exception as e:
        return {"error": str(e)}


def get_trend_indicators(
    symbol: str,
    interval: str = "15minute",
    days: int = 30,
    exchange: str = "NSE"
) -> Dict:
    """
    Calculate trend-specific indicators (EMA, ADX).
    
    Args:
        symbol: Stock symbol
        interval: Candle interval
        days: Days of history
        exchange: Exchange
        
    Returns:
        Dict with EMA and ADX values
    """
    try:
        candle_data = get_historical_candles(symbol, interval, days, exchange)
        
        if "error" in candle_data:
            return candle_data
        
        high = np.array(candle_data["high"])
        low = np.array(candle_data["low"])
        close = np.array(candle_data["close"])
        
        if len(close) < 50:
            return {"error": "Not enough data for trend calculation"}
        
        # Calculate EMAs
        ema_20 = TechnicalIndicators.calculate_ema(close, 20)
        ema_50 = TechnicalIndicators.calculate_ema(close, 50)
        ema_200 = TechnicalIndicators.calculate_ema(close, 200) if len(close) >= 200 else None
        
        # Calculate ADX
        adx = TechnicalIndicators.calculate_adx(high, low, close)
        
        # Get latest values
        current_price = float(close[-1])
        latest_ema_20 = float(ema_20[~np.isnan(ema_20)][-1]) if len(ema_20[~np.isnan(ema_20)]) > 0 else None
        latest_ema_50 = float(ema_50[~np.isnan(ema_50)][-1]) if len(ema_50[~np.isnan(ema_50)]) > 0 else None
        latest_adx = float(adx[~np.isnan(adx)][-1]) if len(adx[~np.isnan(adx)]) > 0 else None
        
        # Determine trend
        trend_direction = "NEUTRAL"
        if latest_ema_20 and latest_ema_50:
            if current_price > latest_ema_20 > latest_ema_50:
                trend_direction = "BULLISH"
            elif current_price < latest_ema_20 < latest_ema_50:
                trend_direction = "BEARISH"
        
        # Determine strength
        trend_strength = "WEAK"
        if latest_adx:
            if latest_adx > 25:
                trend_strength = "STRONG"
            elif latest_adx > 20:
                trend_strength = "MODERATE"
        
        return {
            "symbol": symbol,
            "interval": interval,
            "current_price": current_price,
            "ema_20": latest_ema_20,
            "ema_50": latest_ema_50,
            "adx": latest_adx,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "ema_alignment": f"Price {'>' if current_price > (latest_ema_20 or 0) else '<'} EMA20 {'>' if (latest_ema_20 or 0) > (latest_ema_50 or 0) else '<'} EMA50"
        }
    except ImportError as e:
        return {"error": f"TA-Lib not installed: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
