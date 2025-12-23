"""
Sentiment Agent

Analyzes news, global market cues, and sector performance to assess
market sentiment for each stock.
"""

from google.adk.agents import LlmAgent
from .prompt import SENTIMENT_AGENT_PROMPT
from app.models.llm_models import agentic_reasoning_llm


# Sentiment agent uses reasoning model for complex sentiment analysis
sentiment_agent = LlmAgent(
    name="SentimentAgent",
    model=agentic_reasoning_llm,
    instruction=SENTIMENT_AGENT_PROMPT,
    output_key="sentiment_signal",
)
