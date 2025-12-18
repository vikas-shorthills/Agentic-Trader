"""Fundamentals Analyst Agent - Financial Analysis"""
from google.adk.agents import LlmAgent
from ..models import agentic_fast_llm
from ..tools import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement
from ..prompt import FUNDAMENTALS_ANALYST_PROMPT, ANALYST_SYSTEM_PROMPT

fundamentals_analyst = LlmAgent(
    name="FundamentalsAnalyst",
    model=agentic_fast_llm,
    instruction=FUNDAMENTALS_ANALYST_PROMPT + "\n\nPrevious context (if available):\nMarket Analysis: {{market_report}}\nSentiment Analysis: {{sentiment_report}}",
    tools=[get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement],
    output_key="fundamentals_report"
)
