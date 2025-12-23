"""
News Prefetch Utility
Fetches and caches news for companies listed in the Nifty 100 Excel file.
Stores results in app/utils/data/NSE/<company_ticker>.json format.
"""
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import time
from duckduckgo_search import DDGS
import trafilatura
import requests
from urllib.parse import urlparse

# =============================================================================
# CONFIGURATION - Modify these paths if needed
# =============================================================================
EXCEL_FILE_PATH = "../../artifacts/nifty200_companies.xlsx"  # Relative to app/utils/
OUTPUT_DIR = "data_200/NSE"  # Relative to app/utils/
DEFAULT_DELAY_SECONDS = 2  # Delay between requests
DEFAULT_MAX_RESULTS_PER_COMPANY = 20  # Max news articles per company
ARTICLE_EXTRACTION_TIMEOUT = 10  # Timeout for article download in seconds
# =============================================================================


def load_company_list(excel_path: str = None):
    """Load company list from Excel file"""
    if excel_path is None:
        # Get absolute path relative to this script's location
        script_dir = Path(__file__).parent
        excel_path = str(script_dir / EXCEL_FILE_PATH)
    
    try:
        df = pd.read_excel(excel_path)
        print(f"✓ Loaded {len(df)} companies from {excel_path}")
        print(f"  Columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        print(f"✗ Error loading Excel file: {e}")
        return None

def extract_article_content(url: str, timeout: int = None):
    """
    Extract full article content from URL using trafilatura
    
    Args:
        url: Article URL
        timeout: Request timeout in seconds (uses ARTICLE_EXTRACTION_TIMEOUT if None)
        
    Returns:
        Extracted article text or None if failed
    """
    if timeout is None:
        timeout = ARTICLE_EXTRACTION_TIMEOUT
    
    try:
        # Download the webpage
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Extract main content using trafilatura
        downloaded = response.text
        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False
        )
        
        if content and len(content) > 100:  # Ensure we got meaningful content
            return content
        else:
            return None
            
    except Exception as e:
        # Silently fail - we'll use the snippet if full content extraction fails
        return None

def fetch_news_for_company(ticker: str, company_name: str = None, days_back: int = 30, max_results: int = None):
    """
    Fetch news for a single company using DuckDuckGo search
    AND extract full article content from each URL
    
    Args:
        ticker: Stock ticker (e.g., 'TCS', 'INFY')
        company_name: Full company name (optional, helps with search)
        days_back: Number of days to look back (default: 30)
        max_results: Max articles to fetch (uses DEFAULT_MAX_RESULTS_PER_COMPANY if None)
    
    Returns:
        List of news articles as dictionaries with full content
    """
    if max_results is None:
        max_results = DEFAULT_MAX_RESULTS_PER_COMPANY
    
    try:
        # Build search query
        if company_name:
            query = f"{company_name} {ticker} stock news financial India"
        else:
            query = f"{ticker} stock news financial India"
        
        print(f"  Searching: {query}")
        
        # Fetch news using DuckDuckGo
        ddgs = DDGS()
        results = ddgs.news(keywords=query, region="in-en", max_results=max_results)
        
        if not results:
            print(f"  ⚠ No news found for {ticker}")
            return []
        
        print(f"  ✓ Found {len(results)} articles, extracting full content...")
        
        # Convert to structured format and extract full content
        news_articles = []
        successful_extractions = 0
        
        for idx, article in enumerate(results, 1):
            url = article.get('url', '')
            
            # Extract full article content
            full_content = None
            if url:
                print(f"    [{idx}/{len(results)}] Extracting: {url[:60]}...")
                full_content = extract_article_content(url)
                if full_content:
                    successful_extractions += 1
                    print(f"      ✓ Extracted {len(full_content)} characters")
                else:
                    print(f"      ⚠ Extraction failed, using snippet")
            
            # Use full content if available, otherwise use snippet
            content_text = full_content if full_content else article.get('body', '')
            
            news_articles.append({
                'title': article.get('title', ''),
                'source': article.get('source', ''),
                'url': url,
                'date': article.get('date', ''),
                'snippet': article.get('body', ''),  # Keep original snippet
                'full_content': content_text,  # Full extracted content or snippet
                'content_length': len(content_text),
                'extraction_successful': full_content is not None,
                'fetched_at': datetime.now().isoformat()
            })
        
        print(f"  ✓ Successfully extracted full content for {successful_extractions}/{len(results)} articles")
        return news_articles
        
    except Exception as e:
        print(f"  ✗ Error fetching news for {ticker}: {e}")
        return []

def save_news_to_json(ticker: str, news_data: list, output_dir: str = None):
    """
    Save news data to JSON file
    
    Args:
        ticker: Stock ticker
        news_data: List of news articles
        output_dir: Output directory path (uses OUTPUT_DIR if None)
    """
    if output_dir is None:
        # Get absolute path relative to this script's location
        script_dir = Path(__file__).parent
        output_dir = str(script_dir / OUTPUT_DIR)
    
    try:
        # Create directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Prepare file path
        file_path = os.path.join(output_dir, f"{ticker}.json")
        
        # Prepare metadata
        data_to_save = {
            'ticker': ticker,
            'fetched_at': datetime.now().isoformat(),
            'article_count': len(news_data),
            'articles': news_data
        }
        
        # Save to JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Saved to {file_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error saving {ticker}: {e}")
        return False

def prefetch_all_news(
    excel_path: str = None,
    output_dir: str = None,
    delay_seconds: int = None,
    max_companies: int = None
):
    """
    Main function to prefetch news for all companies
    
    Args:
        excel_path: Path to Excel file (uses EXCEL_FILE_PATH if None)
        output_dir: Directory to save JSON files (uses OUTPUT_DIR if None)
        delay_seconds: Delay between requests (uses DEFAULT_DELAY_SECONDS if None)
        max_companies: Maximum number of companies to process (None = all)
    """
    if delay_seconds is None:
        delay_seconds = DEFAULT_DELAY_SECONDS
    print("=" * 80)
    print("NEWS PREFETCH UTILITY")
    print("=" * 80)
    print()
    
    # Load company list
    df = load_company_list(excel_path)
    if df is None:
        return
    
    print()
    print(f"First few rows:")
    print(df.head())
    print()
    
    # Identify ticker and company name columns
    # Common column names: 'Symbol', 'Ticker', 'Company Name', 'Name'
    ticker_col = None
    name_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'symbol' in col_lower or 'ticker' in col_lower:
            ticker_col = col
        if 'company' in col_lower or 'name' in col_lower:
            name_col = col
    
    if ticker_col is None:
        print("✗ Could not identify ticker column. Please check Excel file.")
        print(f"  Available columns: {df.columns.tolist()}")
        return
    
    print(f"✓ Using columns:")
    print(f"  Ticker: {ticker_col}")
    print(f"  Company Name: {name_col if name_col else 'Not found'}")
    print()
    
    # Limit companies if specified
    companies_to_process = df.head(max_companies) if max_companies else df
    
    print(f"Processing {len(companies_to_process)} companies...")
    print("=" * 80)
    print()
    
    # Process each company
    success_count = 0
    fail_count = 0
    
    for idx, row in companies_to_process.iterrows():
        ticker = str(row[ticker_col]).strip()
        company_name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else None
        
        print(f"[{idx+1}/{len(companies_to_process)}] Processing: {ticker}" + 
              (f" ({company_name})" if company_name else ""))
        
        # Fetch news
        news_data = fetch_news_for_company(ticker, company_name)
        
        # Save to JSON
        if news_data:
            if save_news_to_json(ticker, news_data, output_dir):
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
        
        print()
        
        # Delay to avoid rate limiting
        if idx < len(companies_to_process) - 1:  # Don't delay after last company
            time.sleep(delay_seconds)
    
    # Summary
    print("=" * 80)
    print("PREFETCH COMPLETE")
    print("=" * 80)
    print(f"✓ Success: {success_count} companies")
    print(f"✗ Failed: {fail_count} companies")
    print(f"📁 Data saved to: {output_dir}")
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Prefetch news for NSE companies")
    parser.add_argument(
        '--excel', 
        default=None,
        help=f'Path to Excel file with company list (default: {EXCEL_FILE_PATH})'
    )
    parser.add_argument(
        '--output', 
        default=None,
        help=f'Output directory for JSON files (default: {OUTPUT_DIR})'
    )
    parser.add_argument(
        '--delay', 
        type=int,
        default=None,
        help=f'Delay between requests in seconds (default: {DEFAULT_DELAY_SECONDS})'
    )
    parser.add_argument(
        '--max', 
        type=int,
        default=None,
        help='Maximum number of companies to process (default: all)'
    )
    
    args = parser.parse_args()
    
    # Run prefetch
    prefetch_all_news(
        excel_path=args.excel,
        output_dir=args.output,
        delay_seconds=args.delay,
        max_companies=args.max
    )
