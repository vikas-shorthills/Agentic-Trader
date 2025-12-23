"""
Indicator Agent

Analyzes 5-minute timeframe technical indicators (RSI, MACD, Bollinger, etc.)
to identify potential trading setups.
"""

from google.adk.agents import LlmAgent
from .prompt import INDICATOR_AGENT_PROMPT
from .tools import get_oscillator_indicators
from app.models.llm_models import agentic_fast_llm


indicator_agent = LlmAgent(
    name="IndicatorAgent",
    model=agentic_fast_llm,
    instruction=INDICATOR_AGENT_PROMPT,
    tools=[get_oscillator_indicators],
    output_key="indicator_analysis",
)
