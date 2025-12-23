"""
Technical Indicators Engine using TA-Lib

This module provides wrapper functions for calculating technical indicators
used by the Trading Agent system. All functions take pandas Series or numpy
arrays as input and return the calculated indicator values.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Try to import talib, provide fallback message if not available
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("WARNING: TA-Lib not installed. Install with: pip install TA-Lib")
    print("Note: TA-Lib requires system library. On macOS: brew install ta-lib")


@dataclass
class MACDResult:
    """MACD calculation result"""
    macd: np.ndarray
    signal: np.ndarray
    histogram: np.ndarray


@dataclass
class BollingerResult:
    """Bollinger Bands calculation result"""
    upper: np.ndarray
    middle: np.ndarray
    lower: np.ndarray


@dataclass
class StochResult:
    """Stochastic calculation result"""
    k: np.ndarray
    d: np.ndarray


@dataclass
class CandlestickPatterns:
    """Detected candlestick patterns"""
    hammer: np.ndarray
    inverted_hammer: np.ndarray
    engulfing: np.ndarray
    doji: np.ndarray
    morning_star: np.ndarray
    evening_star: np.ndarray
    three_white_soldiers: np.ndarray
    three_black_crows: np.ndarray


class TechnicalIndicators:
    """
    Technical Indicators Calculator using TA-Lib
    
    All methods are static and can be called without instantiation.
    Input arrays should be numpy arrays or pandas Series.
    """
    
    # =========================================================================
    # TREND INDICATORS
    # =========================================================================
    
    @staticmethod
    def calculate_ema(close: np.ndarray, period: int = 20) -> np.ndarray:
        """
        Calculate Exponential Moving Average
        
        Args:
            close: Array of closing prices
            period: EMA period (default: 20)
            
        Returns:
            Array of EMA values
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        return talib.EMA(close.astype(float), timeperiod=period)
    
    @staticmethod
    def calculate_sma(close: np.ndarray, period: int = 20) -> np.ndarray:
        """
        Calculate Simple Moving Average
        
        Args:
            close: Array of closing prices
            period: SMA period (default: 20)
            
        Returns:
            Array of SMA values
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        return talib.SMA(close.astype(float), timeperiod=period)
    
    @staticmethod
    def calculate_adx(
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        period: int = 14
    ) -> np.ndarray:
        """
        Calculate Average Directional Index (trend strength)
        
        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices
            period: ADX period (default: 14)
            
        Returns:
            Array of ADX values (0-100, >25 = strong trend)
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        return talib.ADX(
            high.astype(float),
            low.astype(float),
            close.astype(float),
            timeperiod=period
        )
    
    # =========================================================================
    # OSCILLATORS
    # =========================================================================
    
    @staticmethod
    def calculate_rsi(close: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Calculate Relative Strength Index
        
        Args:
            close: Array of closing prices
            period: RSI period (default: 14)
            
        Returns:
            Array of RSI values (0-100)
            - < 30: Oversold
            - > 70: Overbought
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        return talib.RSI(close.astype(float), timeperiod=period)
    
    @staticmethod
    def calculate_macd(
        close: np.ndarray,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> MACDResult:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            close: Array of closing prices
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line period (default: 9)
            
        Returns:
            MACDResult with macd, signal, and histogram arrays
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        macd, signal, hist = talib.MACD(
            close.astype(float),
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period
        )
        return MACDResult(macd=macd, signal=signal, histogram=hist)
    
    @staticmethod
    def calculate_stochastic(
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        k_period: int = 14,
        d_period: int = 3,
        d_type: int = 0
    ) -> StochResult:
        """
        Calculate Stochastic Oscillator
        
        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices
            k_period: %K period (default: 14)
            d_period: %D period (default: 3)
            d_type: Moving average type for %D
            
        Returns:
            StochResult with k and d arrays
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        k, d = talib.STOCH(
            high.astype(float),
            low.astype(float),
            close.astype(float),
            fastk_period=k_period,
            slowk_period=d_period,
            slowk_matype=d_type,
            slowd_period=d_period,
            slowd_matype=d_type
        )
        return StochResult(k=k, d=d)
    
    # =========================================================================
    # VOLATILITY INDICATORS
    # =========================================================================
    
    @staticmethod
    def calculate_bollinger_bands(
        close: np.ndarray,
        period: int = 20,
        std_dev: float = 2.0
    ) -> BollingerResult:
        """
        Calculate Bollinger Bands
        
        Args:
            close: Array of closing prices
            period: Moving average period (default: 20)
            std_dev: Standard deviation multiplier (default: 2.0)
            
        Returns:
            BollingerResult with upper, middle, lower bands
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        upper, middle, lower = talib.BBANDS(
            close.astype(float),
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev,
            matype=0
        )
        return BollingerResult(upper=upper, middle=middle, lower=lower)
    
    @staticmethod
    def calculate_atr(
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        period: int = 14
    ) -> np.ndarray:
        """
        Calculate Average True Range (volatility measure)
        
        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices
            period: ATR period (default: 14)
            
        Returns:
            Array of ATR values
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        return talib.ATR(
            high.astype(float),
            low.astype(float),
            close.astype(float),
            timeperiod=period
        )
    
    # =========================================================================
    # VOLUME INDICATORS
    # =========================================================================
    
    @staticmethod
    def calculate_obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """
        Calculate On-Balance Volume
        
        Args:
            close: Array of closing prices
            volume: Array of volume values
            
        Returns:
            Array of OBV values
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        return talib.OBV(close.astype(float), volume.astype(float))
    
    @staticmethod
    def calculate_volume_sma(volume: np.ndarray, period: int = 20) -> np.ndarray:
        """
        Calculate Volume Simple Moving Average
        
        Args:
            volume: Array of volume values
            period: SMA period (default: 20)
            
        Returns:
            Array of volume SMA values
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        return talib.SMA(volume.astype(float), timeperiod=period)
    
    # =========================================================================
    # VWAP (Volume Weighted Average Price)
    # =========================================================================
    
    @staticmethod
    def calculate_vwap(
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray
    ) -> np.ndarray:
        """
        Calculate Volume Weighted Average Price (session-based)
        
        Note: TA-Lib doesn't have VWAP, so we calculate manually
        
        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices
            volume: Array of volume values
            
        Returns:
            Array of VWAP values
        """
        typical_price = (high + low + close) / 3
        cumulative_tp_vol = np.cumsum(typical_price * volume)
        cumulative_vol = np.cumsum(volume)
        vwap = cumulative_tp_vol / cumulative_vol
        return vwap
    
    # =========================================================================
    # CANDLESTICK PATTERNS
    # =========================================================================
    
    @staticmethod
    def detect_candlestick_patterns(
        open_: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray
    ) -> CandlestickPatterns:
        """
        Detect various candlestick patterns
        
        Args:
            open_: Array of opening prices
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices
            
        Returns:
            CandlestickPatterns with pattern detection arrays
            (positive = bullish, negative = bearish, 0 = no pattern)
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for this function")
        
        o = open_.astype(float)
        h = high.astype(float)
        l = low.astype(float)
        c = close.astype(float)
        
        return CandlestickPatterns(
            hammer=talib.CDLHAMMER(o, h, l, c),
            inverted_hammer=talib.CDLINVERTEDHAMMER(o, h, l, c),
            engulfing=talib.CDLENGULFING(o, h, l, c),
            doji=talib.CDLDOJI(o, h, l, c),
            morning_star=talib.CDLMORNINGSTAR(o, h, l, c),
            evening_star=talib.CDLEVENINGSTAR(o, h, l, c),
            three_white_soldiers=talib.CDL3WHITESOLDIERS(o, h, l, c),
            three_black_crows=talib.CDL3BLACKCROWS(o, h, l, c)
        )
    
    # =========================================================================
    # COMPREHENSIVE ANALYSIS
    # =========================================================================
    
    @classmethod
    def calculate_all_indicators(
        cls,
        open_: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray
    ) -> Dict:
        """
        Calculate all indicators at once
        
        Args:
            open_: Array of opening prices
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices
            volume: Array of volume values
            
        Returns:
            Dictionary with all indicator values
        """
        macd_result = cls.calculate_macd(close)
        bb_result = cls.calculate_bollinger_bands(close)
        stoch_result = cls.calculate_stochastic(high, low, close)
        patterns = cls.detect_candlestick_patterns(open_, high, low, close)
        
        return {
            # Trend
            "ema_20": cls.calculate_ema(close, 20),
            "ema_50": cls.calculate_ema(close, 50),
            "ema_200": cls.calculate_ema(close, 200),
            "sma_20": cls.calculate_sma(close, 20),
            "adx": cls.calculate_adx(high, low, close),
            
            # Oscillators
            "rsi": cls.calculate_rsi(close),
            "macd": macd_result.macd,
            "macd_signal": macd_result.signal,
            "macd_histogram": macd_result.histogram,
            "stoch_k": stoch_result.k,
            "stoch_d": stoch_result.d,
            
            # Volatility
            "bb_upper": bb_result.upper,
            "bb_middle": bb_result.middle,
            "bb_lower": bb_result.lower,
            "atr": cls.calculate_atr(high, low, close),
            
            # Volume
            "obv": cls.calculate_obv(close, volume),
            "volume_sma": cls.calculate_volume_sma(volume),
            "vwap": cls.calculate_vwap(high, low, close, volume),
            
            # Patterns
            "patterns": {
                "hammer": patterns.hammer,
                "inverted_hammer": patterns.inverted_hammer,
                "engulfing": patterns.engulfing,
                "doji": patterns.doji,
                "morning_star": patterns.morning_star,
                "evening_star": patterns.evening_star,
                "three_white_soldiers": patterns.three_white_soldiers,
                "three_black_crows": patterns.three_black_crows,
            }
        }
    
    @classmethod
    def get_latest_indicators(
        cls,
        open_: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray
    ) -> Dict:
        """
        Get only the latest (most recent) indicator values
        
        Useful for real-time trading decisions
        
        Args:
            open_: Array of opening prices
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices
            volume: Array of volume values
            
        Returns:
            Dictionary with latest indicator values (scalars, not arrays)
        """
        all_indicators = cls.calculate_all_indicators(open_, high, low, close, volume)
        
        def get_last(arr):
            """Get last non-NaN value from array"""
            if arr is None:
                return None
            valid = arr[~np.isnan(arr)]
            return float(valid[-1]) if len(valid) > 0 else None
        
        latest = {}
        for key, value in all_indicators.items():
            if key == "patterns":
                latest["patterns"] = {
                    k: int(v[-1]) if len(v) > 0 else 0
                    for k, v in value.items()
                }
            else:
                latest[key] = get_last(value)
        
        # Add derived signals
        if latest.get("rsi") is not None:
            rsi = latest["rsi"]
            latest["rsi_signal"] = "OVERSOLD" if rsi < 30 else ("OVERBOUGHT" if rsi > 70 else "NEUTRAL")
        
        if latest.get("macd") is not None and latest.get("macd_signal") is not None:
            latest["macd_crossover"] = "BULLISH" if latest["macd"] > latest["macd_signal"] else "BEARISH"
        
        if latest.get("adx") is not None:
            adx = latest["adx"]
            latest["trend_strength"] = "STRONG" if adx > 25 else ("WEAK" if adx < 20 else "MODERATE")
        
        return latest
