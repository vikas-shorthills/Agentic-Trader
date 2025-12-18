"""
LLM Models Configuration for Investment Agent
Defines the LiteLLM models used by all sub-agents
"""
import os
from google.adk.models.lite_llm import LiteLlm
import litellm

# Enable the use_litellm_proxy flag
litellm.use_litellm_proxy = True

# Load configuration from environment variables
LITELLM_PROXY_API_KEY = os.getenv("LITELLM_PROXY_API_KEY", "***REMOVED_API_KEY***")
LITELLM_PROXY_API_BASE = os.getenv("LITELLM_PROXY_API_BASE", "***REMOVED_URL***")
LITELLM_MODEL = os.getenv("LITELLM_MODEL", "gemini-2.5-flash")

# Fast LLM for quick analysis tasks
agentic_fast_llm = LiteLlm(
    model=LITELLM_MODEL,
    api_key=LITELLM_PROXY_API_KEY,
    base_url=LITELLM_PROXY_API_BASE
)

# Reasoning LLM for complex decision-making tasks
agentic_reasoning_llm = LiteLlm(
    model="gemini-2.5-pro",
    api_key=LITELLM_PROXY_API_KEY,
    base_url=LITELLM_PROXY_API_BASE
)

