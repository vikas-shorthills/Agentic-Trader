"""Market Analyst Agent - Technical Analysis"""
from google.adk.agents import LlmAgent
from ..models import agentic_fast_llm
from ..tools import get_stock_data, get_indicators
from ..prompt import MARKET_ANALYST_PROMPT, ANALYST_SYSTEM_PROMPT

market_analyst = LlmAgent(
    name="MarketAnalyst",
    model=agentic_fast_llm,
    instruction=MARKET_ANALYST_PROMPT,
    tools=[get_stock_data, get_indicators],
    output_key="market_report"
)
