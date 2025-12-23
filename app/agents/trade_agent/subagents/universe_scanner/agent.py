"""
Universe Scanner Agent

Validates and filters user-selected stocks for suitability in intraday trading.
Rejects illiquid, manipulated, or unsuitable stocks.
"""

from google.adk.agents import LlmAgent
from .prompt import UNIVERSE_SCANNER_PROMPT
from .tools import get_stock_quote, get_volume_analysis
from app.models.llm_models import agentic_fast_llm


universe_scanner = LlmAgent(
    name="UniverseScanner",
    model=agentic_fast_llm,
    instruction=UNIVERSE_SCANNER_PROMPT,
    tools=[get_stock_quote, get_volume_analysis],
    output_key="universe_scan_result",
)
