"""
Investment Agent Tools
Stock data fetching tools for ADK agents
Uses Google News for reliable news fetching
"""
import yfinance as yf
import pandas as pd
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.services.zerodha_service import get_zerodha_service
from .googlenews_utils import getNewsData, getGlobalNewsData

#Stock data and Indicators - Used by MarketAnalyst
def get_stock_data(ticker: str, start_date: str, end_date: str) -> str:
    """
    Get historical stock price data
    Uses Zerodha for Indian stocks (NSE/BSE), falls back to yfinance for others
    
    Args:
        ticker: Stock ticker symbol (e.g., 'INFY' for Indian, 'AAPL' for US)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        CSV string with OHLCV data
    """
    try:
        # Try Zerodha first for Indian stocks
        try:
            zerodha = get_zerodha_service()
            
            # Get instruments to find instrument_token
            instruments = zerodha.get_instruments("NSE")
            instrument = next((i for i in instruments if i['tradingsymbol'] == ticker.upper()), None)
            
            if instrument:
                # Get historical data from Zerodha
                historical_data = zerodha.get_historical_data(
                    instrument_token=instrument['instrument_token'],
                    from_date=start_date,
                    to_date=end_date,
                    interval="day"
                )
                
                if historical_data:
                    # Convert to DataFrame
                    df = pd.DataFrame(historical_data)
                    df.set_index('date', inplace=True)
                    csv_data = df.to_csv()
                    return f"Stock data for {ticker} (Zerodha/NSE):\n{csv_data}"
        except Exception as zerodha_error:
            # Fallback to yfinance
            pass
        
        # Use yfinance as fallback or for non-Indian stocks
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if len(hist) == 0:
            return f"No data available for {ticker} between {start_date} and {end_date}"
        
        csv_data = hist.to_csv()
        return f"Stock data for {ticker} (yfinance):\n{csv_data}"
        
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"


def get_indicators(ticker: str, date: str, indicators: List[str]) -> str:
    """
    Calculate technical indicators for a stock
    Uses Zerodha for Indian stocks, yfinance for others
    
    Args:
        ticker: Stock ticker symbol
        date: Current date in YYYY-MM-DD format
        indicators: List of indicator names (e.g., ['rsi', 'macd', 'boll'])
        
    Returns:
        String with calculated indicator values
    """
    try:
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=200)  # Get enough history for indicators
        
        # Try to get data from Zerodha first
        hist = None
        try:
            zerodha = get_zerodha_service()
            instruments = zerodha.get_instruments("NSE")
            instrument = next((i for i in instruments if i['tradingsymbol'] == ticker.upper()), None)
            
            if instrument:
                historical_data = zerodha.get_historical_data(
                    instrument_token=instrument['instrument_token'],
                    from_date=start_date.strftime("%Y-%m-%d"),
                    to_date=end_date.strftime("%Y-%m-%d"),
                    interval="day"
                )
                if historical_data:
                    hist = pd.DataFrame(historical_data)
                    hist.set_index('date', inplace=True)
                    # Rename columns to match yfinance format
                    hist.rename(columns={
                        'open': 'Open',
                        'high': 'High',
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume'
                    }, inplace=True)
        except:
            pass
        
        # Fallback to yfinance if Zerodha fails
        if hist is None or len(hist) == 0:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date.strftime("%Y-%m-%d"), 
                               end=end_date.strftime("%Y-%m-%d"))
        
        if len(hist) == 0:
            return f"No data available for {ticker}"
        
        results = {}
        
        # RSI Calculation
        if 'rsi' in indicators:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            results['rsi'] = float(rsi.iloc[-1]) if len(rsi) > 0 else None
        
        # MACD Calculation
        if any(ind in indicators for ind in ['macd', 'macds', 'macdh']):
            exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal
            
            if 'macd' in indicators:
                results['macd'] = float(macd.iloc[-1]) if len(macd) > 0 else None
            if 'macds' in indicators:
                results['macds'] = float(signal.iloc[-1]) if len(signal) > 0 else None
            if 'macdh' in indicators:
                results['macdh'] = float(histogram.iloc[-1]) if len(histogram) > 0 else None
        
        # Bollinger Bands
        if any(ind in indicators for ind in ['boll', 'boll_ub', 'boll_lb']):
            sma_20 = hist['Close'].rolling(window=20).mean()
            std_20 = hist['Close'].rolling(window=20).std()
            upper_band = sma_20 + (std_20 * 2)
            lower_band = sma_20 - (std_20 * 2)
            
            if 'boll' in indicators:
                results['boll'] = float(sma_20.iloc[-1]) if len(sma_20) > 0 else None
            if 'boll_ub' in indicators:
                results['boll_ub'] = float(upper_band.iloc[-1]) if len(upper_band) > 0 else None
            if 'boll_lb' in indicators:
                results['boll_lb'] = float(lower_band.iloc[-1]) if len(lower_band) > 0 else None
        
        # Moving Averages
        if 'close_10_ema' in indicators:
            ema_10 = hist['Close'].ewm(span=10, adjust=False).mean()
            results['close_10_ema'] = float(ema_10.iloc[-1]) if len(ema_10) > 0 else None
        
        if 'close_50_sma' in indicators:
            sma_50 = hist['Close'].rolling(window=50).mean()
            results['close_50_sma'] = float(sma_50.iloc[-1]) if len(sma_50) > 0 else None
        
        if 'close_200_sma' in indicators:
            sma_200 = hist['Close'].rolling(window=200).mean()
            results['close_200_sma'] = float(sma_200.iloc[-1]) if len(sma_200) > 0 else None
        
        # ATR
        if 'atr' in indicators:
            high_low = hist['High'] - hist['Low']
            high_close = abs(hist['High'] - hist['Close'].shift())
            low_close = abs(hist['Low'] - hist['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(14).mean()
            results['atr'] = float(atr.iloc[-1]) if len(atr) > 0 else None
        
        # VWMA
        if 'vwma' in indicators:
            vwma = (hist['Close'] * hist['Volume']).rolling(window=20).sum() / hist['Volume'].rolling(window=20).sum()
            results['vwma'] = float(vwma.iloc[-1]) if len(vwma) > 0 else None
        
        # Format output
        output = f"Technical Indicators for {ticker} on {date}:\n"
        for indicator, value in results.items():
            output += f"- {indicator}: {value}\n"
        
        return output
        
    except Exception as e:
        return f"Error calculating indicators: {str(e)}"

#News - Used by SocialMediaAnalyst and NewsAnalyst
def get_news(ticker: str, start_date: str, end_date: str) -> str:
    """
    Get company-specific news using Google News (yfinance is broken)
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'INFY')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        String with news articles from Google News
    """
    try:
        # Get company info for better search query
        yf_ticker = ticker
        if not ('.' in ticker or '^' in ticker):  # Indian stock
            yf_ticker = f"{ticker}.NS"
        
        # Try to get company name for better search
        try:
            stock = yf.Ticker(yf_ticker)
            company_name = stock.info.get('longName', ticker)
            # Use both company name and ticker for better results
            query = f"{company_name} stock {ticker}"
        except:
            # Fallback to just ticker
            query = f"{ticker} stock news"
        
        # Fetch news from Google News
        news_results = getNewsData(query, start_date, end_date, max_results=15)
        
        if not news_results:
            return f"No news found for {ticker} ({start_date} to {end_date}). The company may not have recent news coverage."
        
        output = f"News for {ticker} ({start_date} to {end_date}) from Google News:\n\n"
        
        for i, article in enumerate(news_results[:10], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            link = article.get('link', 'No link')
            date = article.get('date', 'Unknown date')
            snippet = article.get('snippet', '')
            
            output += f"{i}. [{date}] {title}\n"
            output += f"   Source: {source}\n"
            output += f"   Summary: {snippet}\n"
            output += f"   Link: {link}\n\n"
        
        return output
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}. Google News may be temporarily unavailable."


def get_global_news(curr_date: str, look_back_days: int = 7, limit: int = 10) -> str:
    """
    Get global financial news using Google News
    Much more reliable than yfinance
    
    Args:
        curr_date: Current date in YYYY-MM-DD format
        look_back_days: Number of days to look back (default: 7)
        limit: Maximum number of articles (default: 10)
        
    Returns:
        String with global market news from Google News
    """
    try:
        # Define search queries for global market news
        queries = [
            "global stock market news",
            "stock market today",
            "financial markets",
            "economy news",
            "India stock market SENSEX NIFTY",
            "Wall Street news"
        ]
        
        # Fetch news from Google News
        news_results = getGlobalNewsData(queries, curr_date, look_back_days, limit=limit)
        
        if not news_results:
            return f"No global market news found for the specified period. Google News may be temporarily unavailable or rate limiting."
        
        output = f"Global Market News ({curr_date}, past {look_back_days} days) from Google News:\n\n"
        
        for i, article in enumerate(news_results[:limit], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            link = article.get('link', 'No link')
            date = article.get('date', 'Unknown date')
            snippet = article.get('snippet', '')
            
            output += f"{i}. [{date}] {title}\n"
            output += f"   Source: {source}\n"
            output += f"   Summary: {snippet}\n"
            output += f"   Link: {link}\n\n"
        
        return output
    except Exception as e:
        return f"Error fetching global news: {str(e)}. Google News may be temporarily unavailable or rate limiting."

#Company Fundamentals - Used by FundamentalAnalyst
def get_fundamentals(ticker: str) -> str:
    """
    Get fundamental data for a stock
    Combines Zerodha quote data with yfinance comprehensive fundamentals
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        String with fundamental metrics
    """
    try:
        output = f"Fundamental data for {ticker}:\n\n"
        
        # Try to get real-time data from Zerodha for Indian stocks
        try:
            zerodha = get_zerodha_service()
            instruments = zerodha.get_instruments("NSE")
            instrument = next((i for i in instruments if i['tradingsymbol'] == ticker.upper()), None)
            
            if instrument:
                # Get current quote
                quote_data = zerodha.get_quote([f"NSE:{ticker.upper()}"])
                if quote_data and f"NSE:{ticker.upper()}" in quote_data:
                    quote = quote_data[f"NSE:{ticker.upper()}"]
                    output += "=== Live Market Data (Zerodha) ===\n"
                    output += f"- Last Price: {quote.get('last_price')}\n"
                    output += f"- Volume: {quote.get('volume')}\n"
                    output += f"- Average Price: {quote.get('average_price')}\n"
                    output += f"- Day High: {quote.get('ohlc', {}).get('high')}\n"
                    output += f"- Day Low: {quote.get('ohlc', {}).get('low')}\n"
                    output += f"- Day Open: {quote.get('ohlc', {}).get('open')}\n"
                    output += f"- Prev Close: {quote.get('ohlc', {}).get('close')}\n"
                    output += "\n"
        except:
            pass
        
        # Get comprehensive fundamentals from yfinance
        # Auto-append .NS for Indian stocks
        yf_ticker = ticker
        if not ('.' in ticker or '^' in ticker):  # No suffix = Indian stock
            yf_ticker = f"{ticker}.NS"
        
        stock = yf.Ticker(yf_ticker)
        info = stock.info
        
        output += "=== Fundamental Metrics (yfinance) ===\n"
        
        # Comprehensive metrics (from best of both versions)
        metrics = {
            'Market Cap': info.get('marketCap'),
            'P/E Ratio (Trailing)': info.get('trailingPE'),
            'Forward P/E': info.get('forwardPE'),
            'PEG Ratio': info.get('pegRatio'),
            'Price to Book': info.get('priceToBook'),
            'EPS (Trailing)': info.get('trailingEps'),
            'EPS (Forward)': info.get('forwardEps'),
            'Revenue (TTM)': info.get('totalRevenue'),
            'Revenue Growth': info.get('revenueGrowth'),
            'Gross Margin': info.get('grossMargins'),
            'Operating Margin': info.get('operatingMargins'),
            'Profit Margin': info.get('profitMargins'),
            'ROE (Return on Equity)': info.get('returnOnEquity'),
            'ROA (Return on Assets)': info.get('returnOnAssets'),
            'Debt to Equity': info.get('debtToEquity'),
            'Current Ratio': info.get('currentRatio'),
            'Quick Ratio': info.get('quickRatio'),
            'Beta': info.get('beta'),
            'Dividend Yield': info.get('dividendYield'),
            '52 Week High': info.get('fiftyTwoWeekHigh'),
            '52 Week Low': info.get('fiftyTwoWeekLow'),
            'Average Volume': info.get('averageVolume'),
        }
        
        for key, value in metrics.items():
            if value is not None:
                # Format large numbers
                if isinstance(value, (int, float)) and value > 1000000:
                    if value > 1000000000:
                        output += f"- {key}: {value/1000000000:.2f}B\n"
                    else:
                        output += f"- {key}: {value/1000000:.2f}M\n"
                else:
                    output += f"- {key}: {value}\n"
        
        return output
    except Exception as e:
        return f"Error fetching fundamentals: {str(e)}"


def get_balance_sheet(ticker: str) -> str:
    """
    Get balance sheet data
    Uses yfinance (auto-appends .NS for Indian stocks)
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE', 'TCS', 'AAPL')
        
    Returns:
        String with balance sheet data
    """
    try:
        # Auto-append .NS for Indian stocks
        yf_ticker = ticker
        if not ('.' in ticker or '^' in ticker):
            yf_ticker = f"{ticker}.NS"
        
        stock = yf.Ticker(yf_ticker)
        balance_sheet = stock.balance_sheet
        
        if balance_sheet.empty:
            return f"No balance sheet data available for {ticker}"
        
        return f"Balance Sheet for {ticker}:\n{balance_sheet.to_string()}"
    except Exception as e:
        return f"Error fetching balance sheet: {str(e)}"


def get_cashflow(ticker: str) -> str:
    """
    Get cash flow statement
    Uses yfinance (auto-appends .NS for Indian stocks)
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE', 'TCS', 'AAPL')
        
    Returns:
        String with cash flow data
    """
    try:
        # Auto-append .NS for Indian stocks
        yf_ticker = ticker
        if not ('.' in ticker or '^' in ticker):
            yf_ticker = f"{ticker}.NS"
        
        stock = yf.Ticker(yf_ticker)
        cashflow = stock.cashflow
        
        if cashflow.empty:
            return f"No cash flow data available for {ticker}"
        
        return f"Cash Flow for {ticker}:\n{cashflow.to_string()}"
    except Exception as e:
        return f"Error fetching cash flow: {str(e)}"


def get_income_statement(ticker: str) -> str:
    """
    Get income statement
    Uses yfinance (auto-appends .NS for Indian stocks)
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE', 'TCS', 'AAPL')
        
    Returns:
        String with income statement data
    """
    try:
        # Auto-append .NS for Indian stocks
        yf_ticker = ticker
        if not ('.' in ticker or '^' in ticker):
            yf_ticker = f"{ticker}.NS"
        
        stock = yf.Ticker(yf_ticker)
        income_stmt = stock.income_stmt
        
        if income_stmt.empty:
            return f"No income statement available for {ticker}"
        
        return f"Income Statement for {ticker}:\n{income_stmt.to_string()}"
    except Exception as e:
        return f"Error fetching income statement: {str(e)}"

