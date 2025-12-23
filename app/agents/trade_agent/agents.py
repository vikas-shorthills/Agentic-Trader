"""
Trade Agent System - Root Agent Definition

Architecture: Optimized flow with parallel analysis phases

Flow:
Phase 1: Universe Validation (Sequential)
  → UniverseScanner filters user-selected stocks

Phase 2: Analysis (PARALLEL) 
  ┌────────────────────────────────────────────────────┐
  │ TechnicalSupervisor │ SentimentAgent │ ManipulationDetector │
  │ (internal parallel) │                │                      │
  └────────────────────────────────────────────────────┘

Phase 3: Decision & Execution (Sequential)
  → StrategyDecider (fuses all signals)
  → RiskManager (position sizing)
  → TradeExecutor (order execution)

Phase 4: EOD Management
  → SquareOffManager (triggered at 3:10 PM)
"""

from google.adk.agents import SequentialAgent, ParallelAgent

from .subagents import (
    universe_scanner,
    technical_supervisor,
    sentiment_agent,
    manipulation_detector,
    strategy_decider,
    risk_manager,
    trade_executor,
    square_off_manager,
)


# =============================================================================
# PARALLEL ANALYSIS PHASE
# =============================================================================
# These 3 agents run CONCURRENTLY since they're independent:
# - technical_supervisor: analyzes price/volume (internally also parallel)
# - sentiment_agent: analyzes news/sentiment
# - manipulation_detector: checks for manipulation

_parallel_analysis = ParallelAgent(
    name="ParallelAnalysisPhase",
    sub_agents=[
        technical_supervisor,    # Has internal parallelism too
        sentiment_agent,
        manipulation_detector,
    ]
)


# =============================================================================
# ROOT AGENT DEFINITION
# =============================================================================

root_agent = SequentialAgent(
    name="trade_agent",
    sub_agents=[
        # ========== PHASE 1: UNIVERSE VALIDATION ==========
        universe_scanner,           # Filter suitable stocks
        
        # ========== PHASE 2: PARALLEL ANALYSIS ==========
        _parallel_analysis,         # Technical + Sentiment + Manipulation
        
        # ========== PHASE 3: DECISION & EXECUTION ==========
        strategy_decider,           # Fuse all signals into decision
        risk_manager,               # Position sizing
        trade_executor,             # Order execution
    ]
)

# Export for ADK to discover
__all__ = ["root_agent"]
