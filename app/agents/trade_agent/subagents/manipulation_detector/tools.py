"""Manipulation Detector Tools"""

from typing import Dict
from datetime import datetime, timedelta
import numpy as np

from app.services.zerodha_service import get_zerodha_service


def analyze_volume_anomalies(symbol: str, exchange: str = "NSE") -> Dict:
    """
    Detect volume anomalies that may indicate manipulation.
    
    Args:
        symbol: Stock symbol
        exchange: Exchange
        
    Returns:
        Dict with volume anomaly analysis
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
        current_price = current_data.get("last_price", 0)
        
        # Get historical data
        instrument_token = zerodha.get_instrument_token(symbol, exchange)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        candles = zerodha.get_historical_data(
            instrument_token=instrument_token,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
            interval="day"
        )
        
        if not candles or len(candles) < 20:
            return {"error": "Not enough historical data"}
        
        volumes = [c["volume"] for c in candles]
        avg_volume = np.mean(volumes[-20:])
        std_volume = np.std(volumes[-20:])
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        volume_zscore = (current_volume - avg_volume) / std_volume if std_volume > 0 else 0
        
        # Check for anomalies
        anomalies = []
        risk_level = "LOW"
        
        if volume_ratio > 5:
            anomalies.append("EXTREME_VOLUME: Volume > 5x average")
            risk_level = "HIGH"
        elif volume_ratio > 3:
            anomalies.append("HIGH_VOLUME: Volume > 3x average")
            risk_level = "MEDIUM"
        
        # Check price movement relative to volume
        price_change_pct = ((current_price - candles[-1]["close"]) / candles[-1]["close"]) * 100
        
        if abs(price_change_pct) > 5 and volume_ratio < 1.5:
            anomalies.append("PRICE_WITHOUT_VOLUME: Large price move on low volume")
            risk_level = "HIGH" if risk_level != "HIGH" else risk_level
        
        return {
            "symbol": symbol,
            "current_volume": current_volume,
            "average_volume": avg_volume,
            "volume_ratio": round(volume_ratio, 2),
            "volume_zscore": round(volume_zscore, 2),
            "price_change_pct": round(price_change_pct, 2),
            "anomalies_detected": anomalies,
            "risk_level": risk_level,
            "recommendation": "DO_NOT_TRADE" if risk_level == "HIGH" else ("CAUTION" if risk_level == "MEDIUM" else "SAFE")
        }
    except Exception as e:
        return {"error": str(e)}


def check_price_manipulation(symbol: str, exchange: str = "NSE") -> Dict:
    """
    Check for price manipulation patterns.
    
    Args:
        symbol: Stock symbol
        exchange: Exchange
        
    Returns:
        Dict with price manipulation analysis
    """
    try:
        zerodha = get_zerodha_service()
        instrument_token = zerodha.get_instrument_token(symbol, exchange)
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=5)
        
        # Get intraday candles
        candles = zerodha.get_historical_data(
            instrument_token=instrument_token,
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d"),
            interval="5minute"
        )
        
        if not candles or len(candles) < 50:
            return {"error": "Not enough intraday data"}
        
        # Analyze recent price action
        recent = candles[-50:]
        
        # Check for erratic price swings
        price_changes = []
        for i in range(1, len(recent)):
            change = abs(recent[i]["close"] - recent[i-1]["close"]) / recent[i-1]["close"] * 100
            price_changes.append(change)
        
        avg_change = np.mean(price_changes)
        max_change = max(price_changes)
        
        patterns_detected = []
        risk_level = "LOW"
        
        # Erratic swings
        if max_change > 2:
            patterns_detected.append("ERRATIC_SWINGS: Large price swings detected")
            risk_level = "MEDIUM"
        
        # Check for gap-up/gap-down without follow-through
        gaps = []
        for i in range(1, len(recent)):
            gap = recent[i]["open"] - recent[i-1]["close"]
            if abs(gap) / recent[i-1]["close"] > 0.005:  # 0.5% gap
                gaps.append(gap)
        
        if len(gaps) > 5:
            patterns_detected.append("FREQUENT_GAPS: Multiple gaps detected")
            risk_level = "MEDIUM"
        
        return {
            "symbol": symbol,
            "avg_price_change_pct": round(avg_change, 3),
            "max_price_change_pct": round(max_change, 3),
            "gap_count": len(gaps),
            "patterns_detected": patterns_detected,
            "risk_level": risk_level,
            "recommendation": "CAUTION" if risk_level == "MEDIUM" else "SAFE"
        }
    except Exception as e:
        return {"error": str(e)}
