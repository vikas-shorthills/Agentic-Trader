"""Risk Manager Agent - Risk Assessment & Mitigation (Synthesizes Risk Debate)"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import RISK_MANAGER_PROMPT

risk_manager = LlmAgent(
    name="RiskManager",
    model=agentic_reasoning_llm,
    instruction=RISK_MANAGER_PROMPT + """

    **Review the conversation history above to find:**
    - Trader's Investment Plan (from Trader)
    - Research Context (from Researcher)
    - Risk Debate Results:
      - Risky Analyst's arguments (high risk/high reward)
      - Conservative Analyst's arguments (low risk/stability)
      - Neutral Analyst's arguments (balanced approach)
      - Risk Judge's evaluation

    Your task: Evaluate the trader's proposal by considering ALL THREE risk perspectives from the debate. Start with the trader's original plan and adjust it based on the most compelling arguments from the risk analysts. Provide a clear, actionable recommendation: Buy, Sell, or Hold. Refine the trader's strategy to balance reward potential with appropriate risk management.""",
    output_key="vetted_strategy"
)
