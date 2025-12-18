"""Researcher Agent - Synthesizes All Analyst Reports AND Debate"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import RESEARCH_MANAGER_PROMPT

researcher = LlmAgent(
    name="Researcher",
    model=agentic_reasoning_llm,
    instruction=RESEARCH_MANAGER_PROMPT + """

    All Analyst Reports Available:

    📊 **Market Analysis Report:**
    {{market_report}}

    💬 **Sentiment Analysis Report:**
    {{sentiment_report}}

    💰 **Fundamentals Analysis Report:**
    {{fundamentals_report}}

    📰 **News Analysis Report:**
    {{news_report}}

    Investment Debate Results:

    🐂 **Bull Analyst's Final Argument (Case for BUY):**
    {{bull_argument}}

    🐻 **Bear Analyst's Final Argument (Case for SELL):**
    {{bear_argument}}

    ⚖️ **Debate Evaluation:**
    {{debate_evaluation}}

    Your task: Synthesize ALL the analyst reports AND the bull/bear debate into a unified investment recommendation. Consider both perspectives from the debate, but make a decisive recommendation based on the strongest arguments. Provide a detailed investment plan for the trader.""",
        output_key="research_report"
    )
