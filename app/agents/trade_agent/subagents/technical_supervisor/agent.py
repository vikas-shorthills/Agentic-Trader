"""
Technical Supervisor Agent

Supervises the Technical Analysis Squad (Trend, Indicator, Pattern, Momentum).
Uses ParallelAgent for concurrent analysis, then fuses outputs into final signal.

Architecture:
┌─────────────────────────────────────────┐
│        ParallelAgent (Analysis)          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│  │  Trend  │ │Indicator│ │ Pattern │    │
│  └─────────┘ └─────────┘ └─────────┘    │
│  ┌─────────┐                            │
│  │Momentum │                            │
│  └─────────┘                            │
└─────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────┐
        │ Technical Fusion  │ (fuses all signals)
        └───────────────────┘
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from .prompt import TECHNICAL_SUPERVISOR_PROMPT
from app.models.llm_models import agentic_reasoning_llm

from .subagents import (
    trend_agent,
    indicator_agent,
    pattern_agent,
    momentum_agent,
)


# Technical analysis fusion agent - uses reasoning model for complex synthesis
_technical_fusion = LlmAgent(
    name="TechnicalFusion",
    model=agentic_reasoning_llm,
    instruction=TECHNICAL_SUPERVISOR_PROMPT,
    output_key="technical_signal",
)

# Parallel agent for concurrent technical analysis
_parallel_analysis = ParallelAgent(
    name="ParallelTechnicalAnalysis",
    sub_agents=[
        trend_agent,       # Analyzes trend direction and strength
        indicator_agent,   # Analyzes oscillators and indicators
        pattern_agent,     # Identifies chart patterns
        momentum_agent,    # Confirms momentum and volume
    ]
)

# The complete Technical Analyst Squad:
# 1. Run all 4 technical agents in PARALLEL
# 2. Then fuse their outputs in the fusion agent
technical_supervisor = SequentialAgent(
    name="TechnicalAnalystSquad",
    sub_agents=[
        _parallel_analysis,  # All 4 agents run concurrently
        _technical_fusion,   # Fuses all outputs into final signal
    ]
)
