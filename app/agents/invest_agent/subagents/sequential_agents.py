"""
Phases 2-5: Sequential Agents
These run one after another, using results from previous steps
"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompts import (
    RESEARCH_MANAGER_PROMPT,
    TRADER_PROMPT,
    RISK_MANAGER_PROMPT,
    PORTFOLIO_MANAGER_PROMPT,
)


# 3. Define the Sequential Specialist Agents
# Use {{key}} to inject results from previous steps into instructions

# Phase 2: Researcher
# Synthesizes all 4 analyst reports
researcher = LlmAgent(
    name="Researcher",
    model=agentic_reasoning_llm,
    instruction="""Synthesize these analyst reports into one comprehensive investment recommendation:

    Market Analysis Report:
    {{market_report}}

    Sentiment Analysis Report:
    {{sentiment_report}}

    Fundamentals Analysis Report:
    {{fundamentals_report}}

    News Analysis Report:
    {{news_report}}

    """ + RESEARCH_MANAGER_PROMPT,
        output_key="research_report"  # Saves to session.state["research_report"]
    )


# Phase 3: Trader
# Makes trade proposal based on research
trader = LlmAgent(
    name="Trader",
    model=agentic_reasoning_llm,
    instruction="""Based on this Research Report, propose a detailed trading strategy:

    Research Report:
    {{research_report}}

    """ + TRADER_PROMPT,
        output_key="trade_strategy"  # Saves to session.state["trade_strategy"]
    )


# Phase 4: Risk Manager
# Reviews trade and adjusts for risk
risk_manager = LlmAgent(
    name="RiskManager",
    model=agentic_reasoning_llm,
    instruction="""Review this trade strategy and adjust for risk and volatility:

    Trade Strategy:
    {{trade_strategy}}

    Research Context:
    {{research_report}}

    """ + RISK_MANAGER_PROMPT,
        output_key="vetted_strategy"  # Saves to session.state["vetted_strategy"]
    )


# Phase 5: Portfolio Manager (Final Decision Maker)
# Makes the FINAL decision
portfolio_manager = LlmAgent(
    name="PortfolioManager",
    model=agentic_reasoning_llm,
    instruction="""Review the final vetted strategy and provide the FINAL executive decision:

    Vetted Strategy:
    {{vetted_strategy}}

    Trade Proposal:
    {{trade_strategy}}

    Research Report:
    {{research_report}}

    """ + PORTFOLIO_MANAGER_PROMPT,
        output_key="final_output"  # Saves to session.state["final_output"]
    )

