"""
Square-Off Manager Agent

Responsible for end-of-day position closure.
Closes all intraday positions before market close.
"""

from google.adk.agents import LlmAgent
from .prompt import SQUARE_OFF_MANAGER_PROMPT
from .tools import get_open_positions, close_position, get_trading_hours_status
from app.models.llm_models import agentic_fast_llm


square_off_manager = LlmAgent(
    name="SquareOffManager",
    model=agentic_fast_llm,
    instruction=SQUARE_OFF_MANAGER_PROMPT,
    tools=[get_open_positions, close_position, get_trading_hours_status],
    output_key="square_off_result",
)
