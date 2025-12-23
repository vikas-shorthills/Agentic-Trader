"""
Trade Agent Subagents Package

Contains all specialized agents for the trading system.
Each subagent has its own folder with:
  - __init__.py
  - agent.py (agent definition)
  - prompt.py (system prompt)
  - tools.py (agent tools, if applicable)

Note: Technical squad agents (trend, indicator, pattern, momentum) are nested
      inside technical_supervisor/subagents/ and run in parallel.
"""

from .universe_scanner import universe_scanner
from .technical_supervisor import technical_supervisor
from .sentiment_agent import sentiment_agent
from .manipulation_detector import manipulation_detector
from .strategy_decider import strategy_decider
from .risk_manager import risk_manager
from .trade_executor import trade_executor
from .square_off_manager import square_off_manager

__all__ = [
    "universe_scanner",
    "technical_supervisor",
    "sentiment_agent",
    "manipulation_detector",
    "strategy_decider",
    "risk_manager",
    "trade_executor",
    "square_off_manager",
]
