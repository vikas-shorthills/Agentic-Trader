from app.config.settings import settings
from google.adk.models.lite_llm import LiteLlm
import litellm
import os
 # e.g., "http://localhost:4000"
# Enable the use_litellm_proxy flag
litellm.use_litellm_proxy = True


agentic_fast_llm = LiteLlm(
        model=settings.litellm_model,
        api_key=settings.LITELLM_PROXY_API_KEY,
        base_url=settings.LITELLM_PROXY_API_BASE
    )
agentic_reasoning_llm = LiteLlm(
    model=settings.litellm_model,
    api_key=settings.LITELLM_PROXY_API_KEY,
    base_url=settings.LITELLM_PROXY_API_BASE
)