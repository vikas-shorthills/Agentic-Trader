"""
Trend Agent

Analyzes higher timeframe (15m/1h) data to determine overall trend direction,
strength, and market regime for trading bias.
"""

from google.adk.agents import LlmAgent
from .prompt import TREND_AGENT_PROMPT
from .tools import get_trend_indicators, get_historical_candles
from app.models.llm_models import agentic_fast_llm


trend_agent = LlmAgent(
    name="TrendAgent",
    model=agentic_fast_llm,
    instruction=TREND_AGENT_PROMPT,
    tools=[get_trend_indicators, get_historical_candles],
    output_key="trend_analysis",
)
