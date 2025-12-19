"""News Analyst Agent - News & Events Analysis"""
from google.adk.agents import LlmAgent
from ..models import agentic_fast_llm
from ..tools import get_news, get_global_news
from ..prompt import NEWS_ANALYST_PROMPT, ANALYST_SYSTEM_PROMPT

news_analyst = LlmAgent(
    name="NewsAnalyst",
    model=agentic_fast_llm,
    instruction=NEWS_ANALYST_PROMPT + "\n\n**Review the conversation history above for previous analyst reports (Market, Sentiment, Fundamentals).**",
    tools=[get_news, get_global_news],
    output_key="news_report"
)
