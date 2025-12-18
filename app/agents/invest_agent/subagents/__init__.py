"""Subagents Package - All Sequential and Debate Agents"""

# Phase 1: Analyst Agents
from .market_analyst import market_analyst
from .social_media_analyst import social_media_analyst
from .fundamentals_analyst import fundamentals_analyst
from .news_analyst import news_analyst

# Phase 2: Investment Debate Agents
from .debate_investment import bull_researcher, bear_researcher, debate_judge

# Phase 3: Synthesis and Trading
from .researcher import researcher
from .trader import trader

# Phase 4: Risk Debate Agents
from .debate_risk import risky_debator, conservative_debator, neutral_debator, risk_judge

# Phase 5: Final Decision
from .risk_manager import risk_manager
from .portfolio_manager import portfolio_manager

__all__ = [
    # Phase 1
    "market_analyst",
    "social_media_analyst",
    "fundamentals_analyst",
    "news_analyst",
    # Phase 2
    "bull_researcher",
    "bear_researcher",
    "debate_judge",
    "researcher",
    # Phase 3
    "trader",
    # Phase 4
    "risky_debator",
    "conservative_debator",
    "neutral_debator",
    "risk_judge",
    "risk_manager",
    # Phase 5
    "portfolio_manager"
]
