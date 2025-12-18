"""Portfolio Manager Agent - Final Investment Decision"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import PORTFOLIO_MANAGER_PROMPT

portfolio_manager = LlmAgent(
    name="PortfolioManager",
    model=agentic_reasoning_llm,
    instruction=PORTFOLIO_MANAGER_PROMPT + """

    All Information Available:

    📈 **Trading Strategy:**
    {{trade_strategy}}

    🔒 **Risk Manager's Assessment:**
    {{vetted_strategy}}

    📊 **Research Report:**
    {{research_report}}

    Make your FINAL, EXECUTABLE investment decision.""",
        output_key="final_output"
    )
