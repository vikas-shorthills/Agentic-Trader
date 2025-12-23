"""
Manipulation Detector Agent

Identifies potential market manipulation including pump-and-dump schemes,
spoofing, and operator-driven movements.
"""

from google.adk.agents import LlmAgent
from .prompt import MANIPULATION_DETECTOR_PROMPT
from .tools import analyze_volume_anomalies, check_price_manipulation
from app.models.llm_models import agentic_fast_llm


manipulation_detector = LlmAgent(
    name="ManipulationDetector",
    model=agentic_fast_llm,
    instruction=MANIPULATION_DETECTOR_PROMPT,
    tools=[analyze_volume_anomalies, check_price_manipulation],
    output_key="manipulation_signal",
)
