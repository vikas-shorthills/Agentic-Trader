"""Portfolio Manager Agent - Final Investment Decision"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import PORTFOLIO_MANAGER_PROMPT

portfolio_manager = LlmAgent(
    name="PortfolioManager",
    model=agentic_reasoning_llm,
    instruction=PORTFOLIO_MANAGER_PROMPT + """

    **Review the conversation history above to find all information:**
    - Trading Strategy (from Trader)
    - Risk Manager's Assessment (from RiskManager)
    - Research Report (from Researcher)
    - All analyst reports and debates

    Make your FINAL, EXECUTABLE investment decision.""",
    output_key="final_output"
)
