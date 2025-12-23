"""
Strategy Decider Agent

Central decision-maker that fuses technical signals, sentiment analysis,
and manipulation risk into final trading decisions.
"""

from google.adk.agents import LlmAgent
from .prompt import STRATEGY_DECIDER_PROMPT
from app.models.llm_models import agentic_reasoning_llm


# Strategy decider uses reasoning model for complex decision-making
strategy_decider = LlmAgent(
    name="StrategyDecider",
    model=agentic_reasoning_llm,
    instruction=STRATEGY_DECIDER_PROMPT,
    output_key="trade_decision",
)
