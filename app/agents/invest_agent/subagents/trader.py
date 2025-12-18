"""Trader Agent - Creates Trading Strategy"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import TRADER_PROMPT

trader = LlmAgent(
    name="Trader",
    model=agentic_reasoning_llm,
    instruction=TRADER_PROMPT + """

    Investment Plan from Research Team:
    {{research_report}}

    Based on this comprehensive analysis, provide your specific trading recommendation and strategy. Remember to end with: FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**""",
        output_key="trade_strategy"
    )
