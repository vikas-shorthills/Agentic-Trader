"""
Risk Manager Agent

Responsible for position sizing and capital allocation based on
risk appetite and portfolio constraints.
"""

from google.adk.agents import LlmAgent
from .prompt import RISK_MANAGER_PROMPT
from .tools import get_portfolio_state, calculate_position_size
from app.models.llm_models import agentic_reasoning_llm


# Risk manager uses reasoning model for complex risk calculations
risk_manager = LlmAgent(
    name="RiskManager",
    model=agentic_reasoning_llm,
    instruction=RISK_MANAGER_PROMPT,
    tools=[get_portfolio_state, calculate_position_size],
    output_key="position_sizing",
)
