"""Investment Debate Agents - Bull vs Bear with Judge

This implements a multi-round debate between Bull (buy) and Bear (sell) analysts.
Each round:
1. Bull makes argument (sees previous Bear argument)
2. Bear counters (sees previous Bull argument)  
3. Judge evaluates both arguments

The debate runs for the full max_iterations (no early termination).
"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import BULL_RESEARCHER_PROMPT, BEAR_RESEARCHER_PROMPT, DEBATE_JUDGE_PROMPT

# Bull Researcher - Argues to BUY
# Sees {{bear_argument}} from previous iteration
bull_researcher = LlmAgent(
    name="BullResearcher",
    model=agentic_reasoning_llm,
    instruction=BULL_RESEARCHER_PROMPT,
    output_key="bull_argument"
)

# Bear Researcher - Argues to SELL  
# Sees {{bull_argument}} from current iteration
bear_researcher = LlmAgent(
    name="BearResearcher",
    model=agentic_reasoning_llm,
    instruction=BEAR_RESEARCHER_PROMPT,
    output_key="bear_argument"
)

# Debate Judge - Evaluates both arguments
debate_judge = LlmAgent(
    name="DebateJudge",
    model=agentic_reasoning_llm,
    instruction=DEBATE_JUDGE_PROMPT,
    output_key="debate_evaluation"
)

