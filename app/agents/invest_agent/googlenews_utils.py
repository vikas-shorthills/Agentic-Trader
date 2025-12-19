"""
Google News Scraper Utility
Adapted from TradingAgents project for reliable news fetching
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_result,
)


def is_rate_limited(response):
    """Check if the response indicates rate limiting (status code 429)"""
    return response.status_code == 429


@retry(
    retry=(retry_if_result(is_rate_limited)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_request(url, headers):
    """Make a request with retry logic for rate limiting"""
    # Random delay before each request to avoid detection
    time.sleep(random.uniform(2, 6))
    response = requests.get(url, headers=headers, timeout=30)
    return response


def getNewsData(query, start_date, end_date, max_results=50):
    """
    Scrape Google News search results for a given query and date range.
    
    Args:
        query: str - search query (e.g., company name, ticker)
        start_date: str - start date in the format yyyy-mm-dd or mm/dd/yyyy
        end_date: str - end date in the format yyyy-mm-dd or mm/dd/yyyy
        max_results: int - maximum number of results to fetch (default 50)
        
    Returns:
        List of dicts with keys: link, title, snippet, date, source
    """
    # Convert date format if needed
    if "-" in start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.strftime("%m/%d/%Y")
    if "-" in end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.strftime("%m/%d/%Y")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    news_results = []
    page = 0
    
    while len(news_results) < max_results:
        offset = page * 10
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws&start={offset}"
        )

        try:
            response = make_request(url, headers)
            soup = BeautifulSoup(response.content, "html.parser")
            results_on_page = soup.select("div.SoaBEf")

            if not results_on_page:
                break  # No more results found

            for el in results_on_page:
                if len(news_results) >= max_results:
                    break
                    
                try:
                    link = el.find("a")["href"]
                    title = el.select_one("div.MBeuO").get_text()
                    snippet = el.select_one(".GI74Re").get_text()
                    date = el.select_one(".LfVVr").get_text()
                    source = el.select_one(".NUnG9d span").get_text()
                    
                    news_results.append(
                        {
                            "link": link,
                            "title": title,
                            "snippet": snippet,
                            "date": date,
                            "source": source,
                        }
                    )
                except Exception as e:
                    # If one of the fields is not found, skip this result
                    continue

            # Check for the "Next" link (pagination)
            next_link = soup.find("a", id="pnnext")
            if not next_link:
                break

            page += 1

        except Exception as e:
            print(f"Google News scraping error: {e}")
            break

    return news_results


def getGlobalNewsData(query_list, curr_date, look_back_days, limit=30):
    """
    Fetch global news from multiple queries
    
    Args:
        query_list: List of search queries (e.g., ["market news", "stock market"])
        curr_date: str - current date in yyyy-mm-dd format
        look_back_days: int - how many days to look back
        limit: int - max results per query
        
    Returns:
        List of news dicts
    """
    from datetime import timedelta
    
    end_date = datetime.strptime(curr_date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=look_back_days)
    start_date = start_date.strftime("%Y-%m-%d")
    
    all_news = []
    for query in query_list:
        try:
            news = getNewsData(query, start_date, curr_date, max_results=limit)
            all_news.extend(news)
        except Exception as e:
            print(f"Error fetching news for query '{query}': {e}")
            continue
    
    return all_news

