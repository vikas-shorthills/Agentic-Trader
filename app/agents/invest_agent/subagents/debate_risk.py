"""Risk Debate Agents - Risky vs Conservative vs Neutral with Judge

This implements a multi-round risk debate between three analysts.
Each round:
1. Risky makes argument (high risk/high reward)
2. Conservative counters (low risk/stability)
3. Neutral provides balance (moderate approach)
4. Risk Judge evaluates all three perspectives

The debate runs for the full max_iterations (no early termination).
"""
from google.adk.agents import LlmAgent
from ..models import agentic_reasoning_llm
from ..prompt import (
    RISKY_DEBATOR_PROMPT,
    CONSERVATIVE_DEBATOR_PROMPT,
    NEUTRAL_DEBATOR_PROMPT,
    RISK_JUDGE_PROMPT
)

# Risky Debator - Advocates for high risk/high reward
# Sees {{conservative_argument}} and {{neutral_argument}} from previous iteration
risky_debator = LlmAgent(
    name="RiskyDebator",
    model=agentic_reasoning_llm,
    instruction=RISKY_DEBATOR_PROMPT,
    output_key="risky_argument"
)

# Conservative Debator - Advocates for low risk/stability
# Sees {{risky_argument}} and {{neutral_argument}}
conservative_debator = LlmAgent(
    name="ConservativeDebator",
    model=agentic_reasoning_llm,
    instruction=CONSERVATIVE_DEBATOR_PROMPT,
    output_key="conservative_argument"
)

# Neutral Debator - Advocates for balanced approach
# Sees {{risky_argument}} and {{conservative_argument}}
neutral_debator = LlmAgent(
    name="NeutralDebator",
    model=agentic_reasoning_llm,
    instruction=NEUTRAL_DEBATOR_PROMPT,
    output_key="neutral_argument"
)

# Risk Judge - Evaluates all three perspectives
risk_judge = LlmAgent(
    name="RiskJudge",
    model=agentic_reasoning_llm,
    instruction=RISK_JUDGE_PROMPT,
    output_key="risk_evaluation"
)

