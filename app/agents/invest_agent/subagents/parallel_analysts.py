"""
Phase 1: Parallel Analysts
4 analysts that run in PARALLEL using ParallelAgent
"""
from google.adk.agents import LlmAgent, ParallelAgent
from ..models import agentic_fast_llm
from ..tools import get_stock_data, get_indicators, get_news, get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_global_news
from ..prompts import (
    MARKET_ANALYST_PROMPT,
    SOCIAL_MEDIA_ANALYST_PROMPT,
    FUNDAMENTALS_ANALYST_PROMPT,
    NEWS_ANALYST_PROMPT,
)


# 1. Define the 4 Parallel Analysts
# Use 'output_key' so their results are saved in the shared session state

market_analyst = LlmAgent(
    name="MarketAnalyst",
    model=agentic_fast_llm,
    instruction=MARKET_ANALYST_PROMPT,
    tools=[get_stock_data, get_indicators],
    output_key="market_report"  # Saves to session.state["market_report"]
)

social_media_analyst = LlmAgent(
    name="SocialMediaAnalyst",
    model=agentic_fast_llm,
    instruction=SOCIAL_MEDIA_ANALYST_PROMPT,
    tools=[get_news],
    output_key="sentiment_report"  # Saves to session.state["sentiment_report"]
)

fundamentals_analyst = LlmAgent(
    name="FundamentalsAnalyst",
    model=agentic_fast_llm,
    instruction=FUNDAMENTALS_ANALYST_PROMPT,
    tools=[get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement],
    output_key="fundamentals_report"  # Saves to session.state["fundamentals_report"]
)

news_analyst = LlmAgent(
    name="NewsAnalyst",
    model=agentic_fast_llm,
    instruction=NEWS_ANALYST_PROMPT,
    tools=[get_news, get_global_news],
    output_key="news_report"  # Saves to session.state["news_report"]
)


# 2. Group them into a ParallelAgent
# This will run all 4 analysts simultaneously
analysis_parallel = ParallelAgent(
    name="ParallelAnalysisLayer",
    sub_agents=[
        market_analyst,
        social_media_analyst,
        fundamentals_analyst,
        news_analyst
    ]
)

