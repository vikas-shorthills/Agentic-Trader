from google.adk import Agent
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import litellm
import os
litellm.use_litellm_proxy = True
 
# Create a proxy-enabled agent (using environment variables)
root_agent = Agent(
    name="invest_agent",
    model=LiteLlm(model="gemini-2.0-flash"), 
    description="Helpfull agent",
    instruction="Greet the incoming user properly and ask for the user's name and age"
)