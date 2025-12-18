"""Social Media & Sentiment Analyst Agent"""
from google.adk.agents import LlmAgent
from ..models import agentic_fast_llm
from ..tools import get_news
from ..prompt import SOCIAL_MEDIA_ANALYST_PROMPT, ANALYST_SYSTEM_PROMPT

social_media_analyst = LlmAgent(
    name="SocialMediaAnalyst",
    model=agentic_fast_llm,
    instruction=SOCIAL_MEDIA_ANALYST_PROMPT + "\n\nPrevious context (if available): {{market_report}}",
    tools=[get_news],
    output_key="sentiment_report"
)
