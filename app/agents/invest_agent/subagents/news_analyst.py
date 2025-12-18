"""News Analyst Agent - News & Events Analysis"""
from google.adk.agents import LlmAgent
from ..models import agentic_fast_llm
from ..tools import get_news, get_global_news
from ..prompt import NEWS_ANALYST_PROMPT, ANALYST_SYSTEM_PROMPT

news_analyst = LlmAgent(
    name="NewsAnalyst",
    model=agentic_fast_llm,
    instruction=NEWS_ANALYST_PROMPT + "\n\nPrevious context (if available):\nMarket Analysis: {{market_report}}\nSentiment Analysis: {{sentiment_report}}\nFundamentals Analysis: {{fundamentals_report}}",
    tools=[get_news, get_global_news],
    output_key="news_report"
)
