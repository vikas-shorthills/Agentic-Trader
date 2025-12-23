"""
Trade Executor Agent

Executes approved trades via Zerodha API, places stop-loss orders,
and handles order management.
"""

from google.adk.agents import LlmAgent
from .prompt import TRADE_EXECUTOR_PROMPT
from .tools import place_trade_order, place_stop_loss_order, get_order_status
from app.models.llm_models import agentic_fast_llm


trade_executor = LlmAgent(
    name="TradeExecutor",
    model=agentic_fast_llm,
    instruction=TRADE_EXECUTOR_PROMPT,
    tools=[place_trade_order, place_stop_loss_order, get_order_status],
    output_key="execution_result",
)
