"""
Momentum Agent

Analyzes 1-minute timeframe for volume confirmation and entry timing.
Validates that momentum supports the trade setup.
"""

from google.adk.agents import LlmAgent
from .prompt import MOMENTUM_AGENT_PROMPT
from .tools import get_realtime_volume, get_price_velocity
from app.models.llm_models import agentic_fast_llm


momentum_agent = LlmAgent(
    name="MomentumAgent",
    model=agentic_fast_llm,
    instruction=MOMENTUM_AGENT_PROMPT,
    tools=[get_realtime_volume, get_price_velocity],
    output_key="momentum_analysis",
)
