"""
Investment Agent Tools
Stock data fetching tools for ADK agents
"""
import yfinance as yf
import pandas as pd
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta


def get_stock_data(ticker: str, start_date: str, end_date: str) -> str:
    """
    Get historical stock price data from yfinance
    
    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        CSV string with OHLCV data
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if len(hist) == 0:
            return f"No data available for {ticker} between {start_date} and {end_date}"
        
        # Convert to CSV format
        csv_data = hist.to_csv()
        return f"Stock data for {ticker}:\n{csv_data}"
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"


def get_indicators(ticker: str, date: str, indicators: List[str]) -> str:
    """
    Calculate technical indicators for a stock
    
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


def get_news(ticker: str, start_date: str, end_date: str) -> str:
    """
    Get news articles for a stock within a date range
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        String with news articles
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news or len(news) == 0:
            return f"No recent news available for {ticker}. The company may have limited news coverage."
        
        # Filter news by date range if timestamps are available
        filtered_news = []
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        for article in news:
            pub_time = article.get('providerPublishTime', None)
            if pub_time:
                pub_dt = datetime.fromtimestamp(pub_time)
                if start_dt <= pub_dt <= end_dt:
                    filtered_news.append(article)
            else:
                # Include articles without timestamps
                filtered_news.append(article)
        
        if not filtered_news:
            filtered_news = news[:10]  # Fallback to recent news
        
        output = f"News for {ticker} ({start_date} to {end_date}):\n\n"
        
        for i, article in enumerate(filtered_news[:10], 1):
            title = article.get('title', 'No title')
            publisher = article.get('publisher', 'Unknown')
            link = article.get('link', 'No link')
            
            pub_time = article.get('providerPublishTime', None)
            if pub_time:
                pub_date = datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M")
                output += f"{i}. [{pub_date}] {title}\n"
            else:
                output += f"{i}. {title}\n"
            
            output += f"   Publisher: {publisher}\n"
            output += f"   Link: {link}\n\n"
        
        return output
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}. Proceeding with available data."


def get_global_news(curr_date: str, look_back_days: int = 7, limit: int = 10) -> str:
    """
    Get global financial news and market trends
    
    Args:
        curr_date: Current date in YYYY-MM-DD format
        look_back_days: Number of days to look back (default: 7)
        limit: Maximum number of articles (default: 10)
        
    Returns:
        String with global market news
    """
    try:
        # Calculate start date
        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=look_back_days)
        
        # Try to get market indices news
        indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ
        global_news = []
        
        for index in indices:
            try:
                ticker = yf.Ticker(index)
                news = ticker.news
                if news:
                    # Filter by date
                    for article in news[:5]:
                        pub_time = article.get('providerPublishTime', None)
                        if pub_time:
                            pub_dt = datetime.fromtimestamp(pub_time)
                            if start_dt <= pub_dt <= end_dt:
                                global_news.append(article)
                        else:
                            global_news.append(article)
            except:
                continue
        
        if global_news:
            output = f"Global Market News ({curr_date}, past {look_back_days} days):\n\n"
            for i, article in enumerate(global_news[:limit], 1):
                title = article.get('title', 'No title')
                publisher = article.get('publisher', 'Unknown')
                pub_time = article.get('providerPublishTime', None)
                if pub_time:
                    pub_date = datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d")
                    output += f"{i}. [{pub_date}] {title}\n   Source: {publisher}\n\n"
                else:
                    output += f"{i}. {title}\n   Source: {publisher}\n\n"
            return output
        else:
            return f"Global market news currently unavailable. Proceeding with company-specific analysis."
    except Exception as e:
        return f"Error fetching global news: {str(e)}. Proceeding with available data."


def get_fundamentals(ticker: str) -> str:
    """
    Get fundamental data for a stock
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        String with fundamental metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        output = f"Fundamental data for {ticker}:\n\n"
        
        # Key metrics
        metrics = {
            'Market Cap': info.get('marketCap'),
            'P/E Ratio': info.get('trailingPE'),
            'Forward P/E': info.get('forwardPE'),
            'EPS': info.get('trailingEps'),
            'Revenue TTM': info.get('totalRevenue'),
            'Revenue Growth': info.get('revenueGrowth'),
            'Profit Margin': info.get('profitMargins'),
            'Operating Margin': info.get('operatingMargins'),
            'ROE': info.get('returnOnEquity'),
            'ROA': info.get('returnOnAssets'),
            'Debt to Equity': info.get('debtToEquity'),
            'Current Ratio': info.get('currentRatio'),
            'Beta': info.get('beta'),
            'Dividend Yield': info.get('dividendYield'),
        }
        
        for key, value in metrics.items():
            if value is not None:
                output += f"- {key}: {value}\n"
        
        return output
    except Exception as e:
        return f"Error fetching fundamentals: {str(e)}"


def get_balance_sheet(ticker: str) -> str:
    """Get balance sheet data"""
    try:
        stock = yf.Ticker(ticker)
        balance_sheet = stock.balance_sheet
        
        if balance_sheet.empty:
            return f"No balance sheet data available for {ticker}"
        
        return f"Balance Sheet for {ticker}:\n{balance_sheet.to_string()}"
    except Exception as e:
        return f"Error fetching balance sheet: {str(e)}"


def get_cashflow(ticker: str) -> str:
    """Get cash flow statement"""
    try:
        stock = yf.Ticker(ticker)
        cashflow = stock.cashflow
        
        if cashflow.empty:
            return f"No cash flow data available for {ticker}"
        
        return f"Cash Flow for {ticker}:\n{cashflow.to_string()}"
    except Exception as e:
        return f"Error fetching cash flow: {str(e)}"


def get_income_statement(ticker: str) -> str:
    """Get income statement"""
    try:
        stock = yf.Ticker(ticker)
        income_stmt = stock.income_stmt
        
        if income_stmt.empty:
            return f"No income statement available for {ticker}"
        
        return f"Income Statement for {ticker}:\n{income_stmt.to_string()}"
    except Exception as e:
        return f"Error fetching income statement: {str(e)}"

