"""
Investment Agent System - Root Orchestrator
SequentialAgent that coordinates the entire workflow
"""
from google.adk.agents import SequentialAgent

# Import the ParallelAgent (Phase 1)
from .subagents.parallel_analysts import analysis_parallel

# Import the Sequential Agents (Phases 2-5)
from .subagents.sequential_agents import (
    researcher,
    trader,
    risk_manager,
    portfolio_manager
)


# 4. Define the Orchestrator (Root Agent)
# This is a SequentialAgent that handles the workflow:
# - First: Run the ParallelAgent (4 analysts in parallel)
# - Then: Run each sequential agent one by one

root_agent = SequentialAgent(
    name="invest_agent",
    sub_agents=[
        analysis_parallel,  # Phase 1: Run all 4 analysts in PARALLEL
        researcher,         # Phase 2: Synthesize reports
        trader,             # Phase 3: Make trade proposal
        risk_manager,       # Phase 4: Risk assessment
        portfolio_manager   # Phase 5: FINAL decision
    ]
)

# Export for ADK to discover
__all__ = ["root_agent"]
