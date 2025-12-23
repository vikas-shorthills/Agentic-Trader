"""
Pydantic Models for Trade Agent System

These models define the structured data types used for communication
between agents and for input/output validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS
# =============================================================================

class TrendDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class TrendStrength(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"


class MarketRegime(str, Enum):
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"


class ManipulationRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"


class ProductType(str, Enum):
    MIS = "MIS"      # Intraday
    CNC = "CNC"      # Delivery
    NRML = "NRML"    # F&O


# =============================================================================
# INPUT MODELS
# =============================================================================

class TradingSession(BaseModel):
    """User input for starting a trading session"""
    stocks: List[str] = Field(..., description="List of stock symbols to trade")
    capital: float = Field(..., description="Total capital available for trading")
    risk_appetite: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Risk appetite (0.0=conservative, 1.0=aggressive)"
    )
    exchange: str = Field(default="NSE", description="Primary exchange")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stocks": ["RELIANCE", "INFY", "TATAMOTORS"],
                "capital": 1000000,
                "risk_appetite": 0.5,
                "exchange": "NSE"
            }
        }


# =============================================================================
# INDICATOR MODELS
# =============================================================================

class IndicatorValues(BaseModel):
    """Current indicator values for a stock"""
    symbol: str
    timeframe: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Price
    current_price: float
    
    # Trend indicators
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    adx: Optional[float] = None
    
    # Oscillators
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    
    # Volatility
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    atr: Optional[float] = None
    
    # Volume
    volume: Optional[float] = None
    volume_sma: Optional[float] = None
    vwap: Optional[float] = None
    
    # Derived signals
    rsi_signal: Optional[str] = None
    macd_crossover: Optional[str] = None
    trend_strength: Optional[str] = None


# =============================================================================
# AGENT OUTPUT MODELS
# =============================================================================

class UniverseScanResult(BaseModel):
    """Output from Universe Scanner Agent"""
    approved_stocks: List[str] = Field(default_factory=list)
    rejected_stocks: List[Dict[str, str]] = Field(default_factory=list)
    reasoning: str


class TrendAnalysis(BaseModel):
    """Output from Trend Agent"""
    symbol: str
    trend_direction: TrendDirection
    trend_strength: TrendStrength
    market_regime: MarketRegime
    trading_bias: str = Field(description="LONG_ONLY, SHORT_ONLY, or BOTH")
    ema_alignment: str
    reasoning: str


class IndicatorAnalysis(BaseModel):
    """Output from Indicator Agent"""
    symbol: str
    indicator_signals: Dict[str, Dict] = Field(
        description="Per-indicator signal with value and score"
    )
    composite_score: float = Field(ge=0.0, le=1.0)
    bias: SignalType
    reasoning: str


class PatternAnalysis(BaseModel):
    """Output from Pattern Agent"""
    symbol: str
    candlestick_pattern: Optional[Dict] = None
    chart_pattern: Optional[Dict] = None
    support_levels: List[float] = Field(default_factory=list)
    resistance_levels: List[float] = Field(default_factory=list)
    reasoning: str


class MomentumAnalysis(BaseModel):
    """Output from Momentum Agent"""
    symbol: str
    momentum_confirmed: bool
    volume_quality: str = Field(description="HIGH, NORMAL, or LOW")
    volume_ratio: float = Field(description="Current volume / Average volume")
    entry_recommendation: str = Field(description="ENTER_NOW, WAIT_PULLBACK, or DONT_ENTER")
    reasoning: str


class TechnicalSignal(BaseModel):
    """Aggregated output from Technical Analyst Supervisor"""
    symbol: str
    signal: SignalType
    confidence: float = Field(ge=0.0, le=1.0)
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    
    # Sub-agent summaries
    trend_summary: str
    indicator_summary: str
    pattern_summary: str
    momentum_summary: str
    
    reasoning: str


class SentimentSignal(BaseModel):
    """Output from Sentiment Agent"""
    symbol: str
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    material_news: bool
    news_headlines: List[str] = Field(default_factory=list)
    global_cues: str
    sector_performance: str
    reasoning: str


class ManipulationSignal(BaseModel):
    """Output from Manipulation Detector Agent"""
    symbol: str
    manipulation_risk: ManipulationRisk
    pattern_detected: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)
    recommendation: str = Field(description="SAFE, CAUTION, or DO_NOT_TRADE")
    reasoning: str


class TradeDecision(BaseModel):
    """Output from Strategy Decider Agent"""
    symbol: str
    action: SignalType
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Input summaries
    technical_signal: str
    sentiment_signal: str
    manipulation_risk: str
    
    conflict_resolution: Optional[str] = None
    reasoning: str


class PositionSizing(BaseModel):
    """Output from Risk Manager Agent"""
    symbol: str
    approved: bool
    
    # If approved
    quantity: Optional[int] = None
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    
    # Capital allocation
    capital_allocated: Optional[float] = None
    capital_percentage: Optional[float] = None
    risk_amount: Optional[float] = None
    risk_percentage: Optional[float] = None
    
    # If rejected
    rejection_reason: Optional[str] = None
    
    reasoning: str


class TradeOrder(BaseModel):
    """Order to be executed"""
    symbol: str
    exchange: str
    transaction_type: str  # BUY or SELL
    quantity: int
    order_type: OrderType
    product: ProductType = ProductType.MIS
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    tag: Optional[str] = None


class ExecutionResult(BaseModel):
    """Output from Trade Executor Agent"""
    symbol: str
    order_id: Optional[str] = None
    status: str  # COMPLETE, PENDING, FAILED
    fill_price: Optional[float] = None
    quantity: int
    
    # SL order
    sl_order_id: Optional[str] = None
    sl_status: Optional[str] = None
    
    error_message: Optional[str] = None
    reasoning: str


class PortfolioState(BaseModel):
    """Current portfolio snapshot"""
    total_capital: float
    available_margin: float
    deployed_capital: float
    reserved_capital: float
    
    positions: List[Dict] = Field(default_factory=list)
    pending_orders: List[Dict] = Field(default_factory=list)
    
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_pnl: float = 0.0
    
    exposure_percentage: float = 0.0


class SquareOffResult(BaseModel):
    """Output from Square-Off Manager"""
    positions_closed: int
    total_realized_pnl: float
    details: List[Dict] = Field(default_factory=list)
    reasoning: str


# =============================================================================
# SESSION STATE
# =============================================================================

class TradingSessionState(BaseModel):
    """Complete trading session state"""
    session_id: str
    started_at: datetime
    
    # User inputs
    selected_stocks: List[str]
    initial_capital: float
    risk_appetite: float
    
    # Current state
    approved_stocks: List[str] = Field(default_factory=list)
    portfolio: Optional[PortfolioState] = None
    
    # Trade history
    trades_executed: List[ExecutionResult] = Field(default_factory=list)
    decisions_made: List[TradeDecision] = Field(default_factory=list)
    
    # Session status
    is_active: bool = True
    squared_off: bool = False
