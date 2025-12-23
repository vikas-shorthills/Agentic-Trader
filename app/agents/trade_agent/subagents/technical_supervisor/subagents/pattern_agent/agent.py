"""
Pattern Agent

Identifies candlestick patterns, support/resistance levels, and chart formations.
"""

from google.adk.agents import LlmAgent
from .prompt import PATTERN_AGENT_PROMPT
from .tools import get_candlestick_patterns, get_support_resistance_levels
from app.models.llm_models import agentic_fast_llm


pattern_agent = LlmAgent(
    name="PatternAgent",
    model=agentic_fast_llm,
    instruction=PATTERN_AGENT_PROMPT,
    tools=[get_candlestick_patterns, get_support_resistance_levels],
    output_key="pattern_analysis",
)
