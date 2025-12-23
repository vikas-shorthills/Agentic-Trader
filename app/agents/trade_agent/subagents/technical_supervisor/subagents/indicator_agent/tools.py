"""Indicator Agent Tools"""

from typing import Dict
from datetime import datetime, timedelta
import numpy as np

from app.services.zerodha_service import get_zerodha_service
from app.services.market_data.indicators import TechnicalIndicators


def get_oscillator_indicators(
    symbol: str,
    interval: str = "5minute",
    days: int = 30,
    exchange: str = "NSE"
) -> Dict:
    """
    Calculate oscillator indicators (RSI, MACD, Stochastic, Bollinger).
    
    Args:
        symbol: Stock symbol
        interval: Candle interval
        days: Days of history
        exchange: Exchange
        
    Returns:
        Dict with indicator values and signals
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
        
        if not candles or len(candles) < 50:
            return {"error": "Not enough data for indicator calculation"}
        
        high = np.array([c["high"] for c in candles])
        low = np.array([c["low"] for c in candles])
        close = np.array([c["close"] for c in candles])
        volume = np.array([c["volume"] for c in candles])
        
        # Calculate indicators
        rsi = TechnicalIndicators.calculate_rsi(close)
        macd_result = TechnicalIndicators.calculate_macd(close)
        bb_result = TechnicalIndicators.calculate_bollinger_bands(close)
        stoch_result = TechnicalIndicators.calculate_stochastic(high, low, close)
        vwap = TechnicalIndicators.calculate_vwap(high, low, close, volume)
        
        # Get latest values
        def get_last(arr):
            valid = arr[~np.isnan(arr)]
            return float(valid[-1]) if len(valid) > 0 else None
        
        current_price = float(close[-1])
        latest_rsi = get_last(rsi)
        latest_macd = get_last(macd_result.macd)
        latest_macd_signal = get_last(macd_result.signal)
        latest_bb_upper = get_last(bb_result.upper)
        latest_bb_lower = get_last(bb_result.lower)
        latest_stoch_k = get_last(stoch_result.k)
        latest_vwap = get_last(vwap)
        
        # Determine signals
        rsi_signal = "OVERSOLD" if latest_rsi and latest_rsi < 30 else ("OVERBOUGHT" if latest_rsi and latest_rsi > 70 else "NEUTRAL")
        macd_signal = "BULLISH" if latest_macd and latest_macd_signal and latest_macd > latest_macd_signal else "BEARISH"
        bb_signal = "OVERSOLD" if latest_bb_lower and current_price <= latest_bb_lower else ("OVERBOUGHT" if latest_bb_upper and current_price >= latest_bb_upper else "NEUTRAL")
        vwap_signal = "BULLISH" if latest_vwap and current_price > latest_vwap else "BEARISH"
        
        # Calculate composite score
        bullish_count = sum([
            rsi_signal == "OVERSOLD",
            macd_signal == "BULLISH",
            bb_signal == "OVERSOLD",
            vwap_signal == "BULLISH"
        ])
        composite_score = bullish_count / 4.0
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "rsi": {"value": latest_rsi, "signal": rsi_signal},
            "macd": {"value": latest_macd, "signal_line": latest_macd_signal, "crossover": macd_signal},
            "bollinger": {"upper": latest_bb_upper, "lower": latest_bb_lower, "signal": bb_signal},
            "stochastic": {"k": latest_stoch_k, "signal": "OVERSOLD" if latest_stoch_k and latest_stoch_k < 20 else ("OVERBOUGHT" if latest_stoch_k and latest_stoch_k > 80 else "NEUTRAL")},
            "vwap": {"value": latest_vwap, "signal": vwap_signal},
            "composite_score": composite_score,
            "overall_bias": "BULLISH" if composite_score > 0.5 else "BEARISH"
        }
    except ImportError as e:
        return {"error": f"TA-Lib not installed: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
