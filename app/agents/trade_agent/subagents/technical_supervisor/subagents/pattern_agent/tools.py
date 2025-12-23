"""Pattern Agent Tools"""

from typing import Dict, List
from datetime import datetime, timedelta
import numpy as np

from app.services.zerodha_service import get_zerodha_service
from app.services.market_data.indicators import TechnicalIndicators


def get_candlestick_patterns(
    symbol: str,
    interval: str = "5minute",
    days: int = 5,
    exchange: str = "NSE"
) -> Dict:
    """
    Detect candlestick patterns in recent candles.
    
    Args:
        symbol: Stock symbol
        interval: Candle interval
        days: Days of history
        exchange: Exchange
        
    Returns:
        Dict with detected patterns
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
        
        if not candles or len(candles) < 10:
            return {"error": "Not enough data for pattern detection"}
        
        open_arr = np.array([c["open"] for c in candles])
        high_arr = np.array([c["high"] for c in candles])
        low_arr = np.array([c["low"] for c in candles])
        close_arr = np.array([c["close"] for c in candles])
        
        patterns = TechnicalIndicators.detect_candlestick_patterns(
            open_arr, high_arr, low_arr, close_arr
        )
        
        # Get latest pattern values
        detected = []
        
        if patterns.hammer[-1] != 0:
            detected.append({"pattern": "Hammer", "signal": "BULLISH", "strength": "MODERATE"})
        if patterns.inverted_hammer[-1] != 0:
            detected.append({"pattern": "Inverted Hammer", "signal": "BULLISH", "strength": "MODERATE"})
        if patterns.engulfing[-1] > 0:
            detected.append({"pattern": "Bullish Engulfing", "signal": "BULLISH", "strength": "STRONG"})
        elif patterns.engulfing[-1] < 0:
            detected.append({"pattern": "Bearish Engulfing", "signal": "BEARISH", "strength": "STRONG"})
        if patterns.doji[-1] != 0:
            detected.append({"pattern": "Doji", "signal": "NEUTRAL", "strength": "WEAK"})
        if patterns.morning_star[-1] != 0:
            detected.append({"pattern": "Morning Star", "signal": "BULLISH", "strength": "STRONG"})
        if patterns.evening_star[-1] != 0:
            detected.append({"pattern": "Evening Star", "signal": "BEARISH", "strength": "STRONG"})
        if patterns.three_white_soldiers[-1] != 0:
            detected.append({"pattern": "Three White Soldiers", "signal": "BULLISH", "strength": "STRONG"})
        if patterns.three_black_crows[-1] != 0:
            detected.append({"pattern": "Three Black Crows", "signal": "BEARISH", "strength": "STRONG"})
        
        return {
            "symbol": symbol,
            "current_price": float(close_arr[-1]),
            "patterns_detected": detected,
            "pattern_count": len(detected),
            "overall_signal": detected[0]["signal"] if detected else "NONE"
        }
    except ImportError as e:
        return {"error": f"TA-Lib not installed: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


def get_support_resistance_levels(
    symbol: str,
    interval: str = "day",
    days: int = 30,
    exchange: str = "NSE"
) -> Dict:
    """
    Calculate support and resistance levels from recent price action.
    
    Args:
        symbol: Stock symbol
        interval: Candle interval
        days: Days of history
        exchange: Exchange
        
    Returns:
        Dict with support and resistance levels
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
        
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        closes = [c["close"] for c in candles]
        current_price = closes[-1]
        
        # Find support levels (recent lows below current price)
        support_levels = sorted([l for l in lows if l < current_price], reverse=True)[:3]
        
        # Find resistance levels (recent highs above current price)
        resistance_levels = sorted([h for h in highs if h > current_price])[:3]
        
        # Round number levels
        def find_round_levels(price, direction="both"):
            levels = []
            base = int(price // 50) * 50
            for i in range(-3, 4):
                level = base + (i * 50)
                if direction == "support" and level < price:
                    levels.append(level)
                elif direction == "resistance" and level > price:
                    levels.append(level)
                elif direction == "both":
                    levels.append(level)
            return levels
        
        round_supports = [l for l in find_round_levels(current_price, "support")][-3:]
        round_resistances = find_round_levels(current_price, "resistance")[:3]
        
        nearest_support = max(support_levels + round_supports) if (support_levels + round_supports) else None
        nearest_resistance = min(resistance_levels + round_resistances) if (resistance_levels + round_resistances) else None
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "support_levels": support_levels[:3],
            "resistance_levels": resistance_levels[:3],
            "round_number_supports": round_supports,
            "round_number_resistances": round_resistances,
            "at_key_level": nearest_support and (current_price - nearest_support) / current_price < 0.01
        }
    except Exception as e:
        return {"error": str(e)}
