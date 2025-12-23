"""Momentum Agent Tools"""

from typing import Dict
from datetime import datetime, timedelta
import numpy as np

from app.services.zerodha_service import get_zerodha_service


def get_realtime_volume(symbol: str, exchange: str = "NSE") -> Dict:
    """
    Get real-time volume analysis for momentum confirmation.
    
    Args:
        symbol: Stock symbol
        exchange: Exchange
        
    Returns:
        Dict with volume metrics and momentum signals
    """
    try:
        zerodha = get_zerodha_service()
        
        # Get current quote
        instrument_key = f"{exchange}:{symbol}"
        quote = zerodha.get_quote([instrument_key])
        
        if instrument_key not in quote:
            return {"error": f"Quote not found for {symbol}"}
        
        current_data = quote[instrument_key]
        current_volume = current_data.get("volume", 0)
        
        # Get historical volume for comparison
        instrument_token = zerodha.get_instrument_token(symbol, exchange)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=20)
        
        candles = zerodha.get_historical_data(
            instrument_token=instrument_token,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
            interval="day"
        )
        
        if not candles or len(candles) < 10:
            return {"error": "Not enough volume history"}
        
        avg_volume = np.mean([c["volume"] for c in candles[-20:]])
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Determine quality
        if volume_ratio > 2.0:
            quality = "HIGH"
            momentum = "STRONG"
            recommendation = "ENTER_NOW"
        elif volume_ratio > 1.5:
            quality = "ABOVE_AVERAGE"
            momentum = "MODERATE"
            recommendation = "ENTER_NOW"
        elif volume_ratio > 1.0:
            quality = "NORMAL"
            momentum = "MODERATE"
            recommendation = "WAIT_PULLBACK"
        else:
            quality = "LOW"
            momentum = "WEAK"
            recommendation = "DONT_ENTER"
        
        return {
            "symbol": symbol,
            "current_price": current_data.get("last_price"),
            "current_volume": current_volume,
            "average_volume": avg_volume,
            "volume_ratio": round(volume_ratio, 2),
            "volume_quality": quality,
            "momentum_strength": momentum,
            "entry_recommendation": recommendation,
            "buy_quantity": current_data.get("buy_quantity"),
            "sell_quantity": current_data.get("sell_quantity"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_price_velocity(
    symbol: str,
    interval: str = "minute",
    candles_count: int = 10,
    exchange: str = "NSE"
) -> Dict:
    """
    Analyze recent price velocity for momentum assessment.
    
    Args:
        symbol: Stock symbol
        interval: Candle interval ('minute' for 1-min)
        candles_count: Number of recent candles to analyze
        exchange: Exchange
        
    Returns:
        Dict with price velocity metrics
    """
    try:
        zerodha = get_zerodha_service()
        instrument_token = zerodha.get_instrument_token(symbol, exchange)
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=1)  # Get today's 1-min data
        
        candles = zerodha.get_historical_data(
            instrument_token=instrument_token,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
            interval=interval
        )
        
        if not candles or len(candles) < candles_count:
            return {"error": "Not enough 1-minute data"}
        
        # Get recent candles
        recent = candles[-candles_count:]
        
        # Calculate candle sizes (high - low)
        candle_sizes = [c["high"] - c["low"] for c in recent]
        
        # Check if candles are getting larger (momentum building) or smaller (fading)
        first_half_avg = np.mean(candle_sizes[:len(candle_sizes)//2])
        second_half_avg = np.mean(candle_sizes[len(candle_sizes)//2:])
        
        if second_half_avg > first_half_avg * 1.2:
            momentum_direction = "BUILDING"
        elif second_half_avg < first_half_avg * 0.8:
            momentum_direction = "FADING"
        else:
            momentum_direction = "STEADY"
        
        # Calculate price change
        price_change = recent[-1]["close"] - recent[0]["open"]
        price_change_pct = (price_change / recent[0]["open"]) * 100
        
        return {
            "symbol": symbol,
            "current_price": recent[-1]["close"],
            "price_change": price_change,
            "price_change_pct": round(price_change_pct, 2),
            "average_candle_size": np.mean(candle_sizes),
            "momentum_direction": momentum_direction,
            "candles_analyzed": candles_count,
            "price_direction": "UP" if price_change > 0 else "DOWN"
        }
    except Exception as e:
        return {"error": str(e)}
