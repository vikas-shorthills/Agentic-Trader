"""
Investment Agent Instructions
Summary of the multi-agent system architecture
"""

SYSTEM_OVERVIEW = """
    # Investment Agent System - Multi-Agent Architecture

    ## System Design
    A comprehensive stock analysis system using 13 AI agents across 5 phases:

    ### Phase 1: Analysts (PARALLEL EXECUTION via sub-agents)
    - **market_analyst**: Technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
    - **social_media_analyst**: Sentiment analysis from social media and news
    - **fundamentals_analyst**: Financial metrics (P/E, EPS, Revenue, Cash Flow)
    - **news_analyst**: News analysis and macroeconomic trends

    **Key Feature**: These 4 analysts are sub-agents of the root_agent, allowing ADK to execute them in PARALLEL for 3.5x speed improvement.

    ### Phase 2: Research Team (Sequential Debate)
    - **bull_researcher**: Builds optimistic investment case
    - **bear_researcher**: Builds pessimistic investment case
    - **research_manager**: Synthesizes balanced recommendation (BUY/SELL/HOLD)

    ### Phase 3: Trader (Sequential)
    - **trader**: Makes initial trade proposal with risk parameters

    ### Phase 4: Risk Management Team (Sequential Debate)
    - **risky_analyst**: Aggressive risk perspective (higher returns)
    - **neutral_analyst**: Balanced risk perspective
    - **safe_analyst**: Conservative risk perspective (capital preservation)
    - **portfolio_manager**: Makes FINAL risk-adjusted decision

    ## Data Sources
    - **yfinance**: Stock prices and technical indicators
    - **Company financials**: Balance sheet, income statement, cash flow
    - **News**: Company-specific and global financial news
    - **Sentiment**: Social media and news sentiment analysis

    ## Agent Tools
    Each analyst has specific tools:
    - Market: get_stock_data, get_indicators
    - Social Media: get_news
    - Fundamentals: get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement
    - News: get_news, get_global_news

    ## Workflow
    1. User asks to analyze a stock (e.g., "Analyze NVDA")
    2. Root agent extracts ticker and date
    3. **Phase 1 analysts run in PARALLEL** (via sub_agents)
    4. Phases 2-4 run sequentially, building on previous outputs
    5. Final decision with specific trading parameters

    ## Output
    - Complete analysis report
    - Final decision: BUY/SELL/HOLD
    - Position size recommendation
    - Entry/exit prices
    - Stop loss and take profit levels
    - Risk/reward analysis
    - Confidence score

    ## Performance
    - Phase 1 parallel execution: ~12 seconds (vs ~42 sequential)
    - Total analysis time: ~20-30 seconds
    - Cost per analysis: ~$0.02-0.05 (using Gemini via LiteLLM)
    """

USAGE_INSTRUCTIONS = """
    ## How to Use

    ### Via ADK Web Interface:
    1. Navigate to the web UI
    2. Send a message like: "Analyze NVDA for today"
    3. The system will:
    - Extract the ticker (NVDA)
    - Use current date if not specified
    - Run the full 5-phase analysis
    - Return comprehensive results

    ### Example Queries:
    - "Analyze AAPL"
    - "What's your take on Tesla stock?"
    - "Should I invest in NVDA today?"
    - "Analyze Microsoft for 2024-12-17"

    ### Via Python API:
    ```python
    from app.agents.invest_agent.agent import root_agent

    # The root agent handles everything
    response = root_agent.run("Analyze NVDA for today")
    ```

    ## Expected Output Format:
    ```
    === INVESTMENT ANALYSIS: NVDA ===

    PHASE 1: ANALYST REPORTS (PARALLEL)
    ✓ Market Analyst: Technical indicators show...
    ✓ Social Media Analyst: Sentiment is...
    ✓ Fundamentals Analyst: Financial health...
    ✓ News Analyst: Recent developments...

    PHASE 2: RESEARCH TEAM
    Bull Case: [Growth potential, competitive advantages...]
    Bear Case: [Risks, concerns, weaknesses...]
    Recommendation: BUY (Confidence: 75%)

    PHASE 3: TRADER PROPOSAL
    Action: BUY
    Position: 10% of portfolio
    Entry: Market order
    Stop Loss: $XXX
    Take Profit: $YYY

    PHASE 4: FINAL DECISION
    FINAL ACTION: BUY
    FINAL POSITION SIZE: 7% of portfolio
    ENTRY PRICE: Market order
    STOP LOSS: $XXX (5% below entry)
    TAKE PROFIT: $YYY (15% above entry)
    EXPECTED RETURN: 12-15%
    MAXIMUM LOSS: 5%
    RATIONALE: [Complete reasoning...]
    ```
    """

