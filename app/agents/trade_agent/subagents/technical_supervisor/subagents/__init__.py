"""Technical Squad Subagents"""
from .trend_agent import trend_agent
from .indicator_agent import indicator_agent
from .pattern_agent import pattern_agent
from .momentum_agent import momentum_agent

__all__ = [
    "trend_agent",
    "indicator_agent",
    "pattern_agent",
    "momentum_agent",
]
