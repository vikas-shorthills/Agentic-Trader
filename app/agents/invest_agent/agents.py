"""
Investment Agent System - WITH DEBATE MECHANISMS
Architecture: Sequential flow with embedded debate loops

Flow:
Phase 1: Analysts (Sequential)
  → Market → Social → Fundamentals → News

Phase 2: Investment Debate (LoopAgent, 3 rounds)
  → [Bull ↔ Bear → Judge] x 3 rounds → Researcher synthesis

Phase 3: Trading Strategy
  → Trader

Phase 4: Risk Debate (LoopAgent, 2 rounds)
  → [Risky ↔ Conservative ↔ Neutral → Risk Judge] x 2 rounds → Risk Manager synthesis

Phase 5: Final Decision
  → Portfolio Manager
"""
from google.adk.agents import SequentialAgent, LoopAgent

# Import Phase 1: Analyst agents
from .subagents import (
    market_analyst,
    social_media_analyst,
    fundamentals_analyst,
    news_analyst
)

# Import Phase 2: Investment debate agents and synthesis
from .subagents import (
    bull_researcher,
    bear_researcher,
    debate_judge,
    researcher
)

# Import Phase 3: Trading
from .subagents import trader

# Import Phase 4: Risk debate agents and synthesis
from .subagents import (
    risky_debator,
    conservative_debator,
    neutral_debator,
    risk_judge,
    risk_manager
)

# Import Phase 5: Final decision
from .subagents import portfolio_manager

# ============================================================================
# DEBATE LOOP DEFINITIONS
# ============================================================================

# Investment Debate Loop: Bull vs Bear (3 rounds)
# Each round: Bull → Bear → Judge
# Runs for full 3 rounds
investment_debate_loop = LoopAgent(
    name="InvestmentDebate",
    max_iterations=3,  # Always runs 3 full rounds
    sub_agents=[
        bull_researcher,    # Argues to BUY (sees {{bear_argument}})
        bear_researcher,    # Argues to SELL (sees {{bull_argument}})
        debate_judge        # Evaluates both arguments
    ]
)

# Risk Debate Loop: Risky vs Conservative vs Neutral (2 rounds)
# Each round: Risky → Conservative → Neutral → Risk Judge
# Runs for full 2 rounds
risk_debate_loop = LoopAgent(
    name="RiskDebate",
    max_iterations=2,  # Always runs 2 full rounds
    sub_agents=[
        risky_debator,          # High risk/reward (sees others)
        conservative_debator,   # Low risk/stability (sees others)
        neutral_debator,        # Balanced approach (sees others)
        risk_judge              # Evaluates all three perspectives
    ]
)

# ============================================================================
# ROOT AGENT DEFINITION
# ============================================================================

root_agent = SequentialAgent(
    name="invest_agent",
    sub_agents=[
        # ========== PHASE 1: ANALYSTS (Sequential) ==========
        market_analyst,          # 1. Technical analysis → market_report
        social_media_analyst,    # 2. Sentiment analysis → sentiment_report
        fundamentals_analyst,    # 3. Financial analysis → fundamentals_report
        news_analyst,            # 4. News & events → news_report
        
        # ========== PHASE 2: INVESTMENT DEBATE (Loop) ==========
        investment_debate_loop,  # 5. Bull vs Bear debate (3 rounds)
                                 #    → bull_argument, bear_argument, debate_evaluation
        researcher,              # 6. Synthesizes all analysts + debate → research_report
        
        # ========== PHASE 3: TRADING STRATEGY ==========
        trader,                  # 7. Creates trading strategy → trade_strategy
        
        # ========== PHASE 4: RISK DEBATE (Loop) ==========
        risk_debate_loop,        # 8. Risky vs Conservative vs Neutral (2 rounds)
                                 #    → risky_argument, conservative_argument, 
                                 #       neutral_argument, risk_evaluation
        risk_manager,            # 9. Synthesizes risk debate → vetted_strategy
        
        # ========== PHASE 5: FINAL DECISION ==========
        portfolio_manager        # 10. Final investment decision → final_output
    ]
)

# Export for ADK to discover
__all__ = ["root_agent"]
