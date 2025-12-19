"""Researcher Agent - Synthesizes All Analyst Reports AND Debate"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import RESEARCH_MANAGER_PROMPT

researcher = LlmAgent(
    name="Researcher",
    model=agentic_reasoning_llm,
    instruction=RESEARCH_MANAGER_PROMPT + """

    **Review the conversation history above to find:**
    - Market Analysis Report (from MarketAnalyst)
    - Sentiment Analysis Report (from SocialMediaAnalyst)
    - Fundamentals Analysis Report (from FundamentalsAnalyst)
    - News Analysis Report (from NewsAnalyst)
    - Bull Analyst's Final Argument (from investment debate)
    - Bear Analyst's Final Argument (from investment debate)
    - Debate Evaluation (from debate judge)

    Your task: Synthesize ALL the analyst reports AND the bull/bear debate into a unified investment recommendation. Consider both perspectives from the debate, but make a decisive recommendation based on the strongest arguments. Provide a detailed investment plan for the trader.""",
    output_key="research_report"
)
