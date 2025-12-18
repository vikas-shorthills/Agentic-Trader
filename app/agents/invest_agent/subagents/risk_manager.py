"""Risk Manager Agent - Risk Assessment & Mitigation (Synthesizes Risk Debate)"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import RISK_MANAGER_PROMPT

risk_manager = LlmAgent(
    name="RiskManager",
    model=agentic_reasoning_llm,
    instruction=RISK_MANAGER_PROMPT + """

    Trader's Investment Plan:
    {{trade_strategy}}

    Research Context:
    {{research_report}}

    Risk Debate Results:

    🚀 **Risky Analyst's Final Argument (High Risk/High Reward):**
    {{risky_argument}}

    🛡️ **Conservative Analyst's Final Argument (Low Risk/Stability):**
    {{conservative_argument}}

    ⚖️ **Neutral Analyst's Final Argument (Balanced Approach):**
    {{neutral_argument}}

    📋 **Risk Debate Evaluation:**
    {{risk_evaluation}}

    Your task: Evaluate the trader's proposal by considering ALL THREE risk perspectives from the debate. Start with the trader's original plan and adjust it based on the most compelling arguments from the risk analysts. Provide a clear, actionable recommendation: Buy, Sell, or Hold. Refine the trader's strategy to balance reward potential with appropriate risk management.""",
        output_key="vetted_strategy"
    )
