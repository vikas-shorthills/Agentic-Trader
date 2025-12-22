import requests
import pandas as pd
import gzip
import io
import re
import hashlib
from urllib.parse import urlencode
import os
# --- CONFIGURATION ---
# NOTE: You need valid credentials from your Zerodha Kite Connect developer account.
# Get these from: https://developers.kite.trade/
# ACCESS_TOKEN is now fetched dynamically via get_access_token()

def get_access_token():
    """
    Get the current access token directly from the session file.
    strictly reads from: /home/shtlp_0170/Videos/hackthon/Agentic-Trader/cache/kite_session.json
    """
    try:
        import json
        from pathlib import Path
        
        session_file = Path("/home/shtlp_0170/Videos/hackthon/Agentic-Trader/cache/kite_session.json")
        
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
                token = data.get("access_token")
                if token:
                    return token
    except Exception as e:
        print(f"⚠️ Error reading token from file: {e}")
        pass
        
    return None


# ---------------------

def generate_access_token(request_token):
    """
    Generate access token using request token, API key, and API secret.
    
    Steps to get request_token:
    1. Go to: https://kite.zerodha.com/connect/login?api_key=YOUR_API_KEY
    2. Login and authorize
    3. You'll be redirected to your redirect_url with request_token in the URL
    4. Extract the request_token from URL parameter
    
    Args:
        request_token (str): The request token obtained after login
        
    Returns:
        dict: Response containing access_token and other details
    """
    url = "https://api.kite.trade/session/token"
    
    # Generate checksum: sha256(api_key + request_token + api_secret)
    checksum_string = API_KEY + request_token + API_SECRET
    checksum = hashlib.sha256(checksum_string.encode()).hexdigest()
    
    payload = {
        "api_key": API_KEY,
        "request_token": request_token,
        "checksum": checksum
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            print(f"Access Token generated: {data['data']['access_token']}")
            print(f"User ID: {data['data']['user_id']}")
            return data['data']
        else:
            print(f"Error generating token: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error generating access token: {e}")
        return None


def fetch_kite_instruments():
    """
    Fetches the complete instrument list from the Kite Connect API.
    
    Requires:
        - Valid API_KEY and ACCESS_TOKEN
        
    Returns:
        pandas.DataFrame: DataFrame containing all instruments
    """
    access_token = get_access_token()
    
    url = "https://api.kite.trade/instruments"
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {API_KEY}:{access_token}"
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        
        # Check if response is successful
        if response.status_code != 200:
            print(f"❌ API Error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"Response: {response.text[:200]}")
            
            if response.status_code == 401:
                print("\n⚠️  Authentication Error: Your ACCESS_TOKEN is invalid or expired.")
                print("ACCESS_TOKEN validity: 24 hours only")
                print("\nTo generate a new access token:")
                print("1. Visit this URL in your browser:")
                print(f"   https://kite.zerodha.com/connect/login?api_key={API_KEY}")
                print("2. Login and authorize")
                print("3. Extract request_token from the redirect URL")
                print("4. Run this command:")
                print(f"   python3 -c \"from companies import generate_access_token; print(generate_access_token('YOUR_REQUEST_TOKEN'))\"")
                print("5. Update ACCESS_TOKEN in companies.py with the new token")
            return None
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        
        # Try to decompress if it's gzipped
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gf:
                csv_data = gf.read().decode('utf-8')
        except gzip.BadGzipFile:
            # If not gzipped, try to decode directly
            print("⚠️  Response is not gzipped, trying direct decode...")
            csv_data = response.content.decode('utf-8')
            
            # Check if it's an error response (HTML or JSON)
            if csv_data.startswith('<') or csv_data.startswith('{'):
                print("❌ Received error response instead of CSV data")
                print(f"Response preview: {csv_data[:500]}")
                print("\n⚠️  This usually means your ACCESS_TOKEN is invalid or expired.")
                print("Please generate a new access token (valid for 24 hours only)")
                return None
        
        df = pd.read_csv(io.StringIO(csv_data))
        return df

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print(f"Error type: {type(e).__name__}")
        return None

def fetch_nifty_index_constituents(index_name):
    """
    Fetch constituents of a specific Nifty index from NSE India API.
    
    Args:
        index_name (str): Name of the index (e.g., 'NIFTY 50', 'NIFTY 100', 'NIFTY 200')
        
    Returns:
        list: List of company symbols in the index
    """
    # NSE India API endpoints for index constituents
    index_urls = {
        'NIFTY 50': 'https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050',
        'NIFTY 100': 'https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100',
        'NIFTY 200': 'https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200',
        'NIFTY MIDCAP 100': 'https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20MIDCAP%20100',
    }
    
    url = index_urls.get(index_name.upper())
    if not url:
        print(f"❌ Index '{index_name}' not found")
        return []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Filter out the index itself - it has priority=1, companies have priority=0
            # This removes "NIFTY 50", "NIFTY 100", "NIFTY 200" from appearing in the lists
            companies = [
                item['symbol'] 
                for item in data.get('data', [])
                if item.get('priority', 0) == 0
            ]
            print(f"✅ Found {len(companies)} {index_name} companies")
            return companies
        else:
            print(f"⚠️  API returned status {response.status_code} for {index_name}")
            return []
    except Exception as e:
        print(f"⚠️  Error fetching {index_name}: {e}")
        return []


def get_nifty50_companies():
    """
    Get list of Nifty 50 companies.
    
    Returns:
        list: List of Nifty 50 company symbols
    """
    print("📊 Fetching Nifty 50 companies...")
    companies = fetch_nifty_index_constituents('NIFTY 50')
    if companies:
        print(f"✅ Found {len(companies)} Nifty 50 companies")
    return companies


def get_nifty100_companies():
    """
    Get list of Nifty 100 companies.
    
    Returns:
        list: List of Nifty 100 company symbols
    """
    print("📊 Fetching Nifty 100 companies...")
    companies = fetch_nifty_index_constituents('NIFTY 100')
    if companies:
        print(f"✅ Found {len(companies)} Nifty 100 companies")
    return companies


def get_nifty200_companies():
    """
    Get list of Nifty 200 companies.
    
    Returns:
        list: List of Nifty 200 company symbols
    """
    print("📊 Fetching Nifty 200 companies...")
    companies = fetch_nifty_index_constituents('NIFTY 200')
    if companies:
        print(f"✅ Found {len(companies)} Nifty 200 companies")
    return companies


def get_all_nse_companies():
    """
    Get list of all NSE equity companies from Kite instruments.
    
    Returns:
        pandas.DataFrame: DataFrame with all NSE equity companies
    """
    print("📊 Fetching all NSE companies...")
    instruments_df = fetch_kite_instruments()
    
    if instruments_df is None or instruments_df.empty:
        print("❌ Failed to fetch instruments")
        return pd.DataFrame()
    
    # Filter for equity stocks on NSE
    nse_eq = instruments_df[
        (instruments_df['exchange'] == 'NSE') & 
        (instruments_df['instrument_type'] == 'EQ')
    ].copy()
    
    # Filter out index names and non-stock instruments
    # Remove entries containing: NIFTY, SENSEX, INDEX, VIX, -NAV, BEES, BHARATBOND
    exclude_patterns = r'NIFTY|SENSEX|INDEX|VIX|-NAV|BEES|BHARATBOND'
    nse_eq = nse_eq[~nse_eq['tradingsymbol'].str.contains(exclude_patterns, case=False, na=False)]
    
    # Also filter by name column to catch any other index-related entries
    nse_eq = nse_eq[~nse_eq['name'].str.contains(exclude_patterns, case=False, na=False)]
    
    print(f"✅ Found {len(nse_eq)} NSE equity companies")
    return nse_eq[['tradingsymbol', 'name', 'instrument_token', 'exchange', 'tick_size', 'lot_size']]


def export_to_json(data, filename):
    """
    Export data to JSON file.
    
    Args:
        data: List or DataFrame to export
        filename (str): Output filename
    """
    import json
    
    if isinstance(data, pd.DataFrame):
        data = data.to_dict('records')
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Data exported to {filename}")


def export_to_csv(data, filename):
    """
    Export data to CSV file.
    
    Args:
        data: List or DataFrame to export
        filename (str): Output filename
    """
    if isinstance(data, list):
        df = pd.DataFrame({'symbol': data})
    else:
        df = data
    
    df.to_csv(filename, index=False)
    print(f"✅ Data exported to {filename}")


# --- EXECUTION ---
if __name__ == "__main__":
    # Check if credentials are configured
    if API_KEY == "YOUR_API_KEY" or API_SECRET == "YOUR_API_SECRET":
        print("❌ Please configure your credentials in the script.")
        print("\nSteps to get Kite Connect credentials:")
        print("1. Go to https://developers.kite.trade/")
        print("2. Create an app to get API_KEY and API_SECRET")
        print("3. Generate ACCESS_TOKEN using the generate_access_token() function")
        print("\nExample usage to generate token:")
        print("  # After getting request_token from login redirect URL:")
        print("  # token_data = generate_access_token('your_request_token_here')")
        print("  # Then update ACCESS_TOKEN in the script")
    else:
        print("=" * 70)
        print("🚀 FETCHING INDIAN STOCK MARKET COMPANY LISTS")
        print("=" * 70)
        print()
        
        # 1. Fetch Nifty 50 companies
        print("1️⃣  NIFTY 50 COMPANIES")
        print("-" * 70)
        nifty50 = get_nifty50_companies()
        if nifty50:
            print(f"   Symbols: {', '.join(nifty50[:10])}...")
            export_to_json(nifty50, 'nifty50_companies.json')
            export_to_csv(nifty50, 'nifty50_companies.csv')
        print()
        
        # 2. Fetch Nifty 100 companies
        print("2️⃣  NIFTY 100 COMPANIES")
        print("-" * 70)
        nifty100 = get_nifty100_companies()
        if nifty100:
            print(f"   Symbols: {', '.join(nifty100[:10])}...")
            export_to_json(nifty100, 'nifty100_companies.json')
            export_to_csv(nifty100, 'nifty100_companies.csv')
        print()
        
        # 3. Fetch Nifty 200 companies
        print("3️⃣  NIFTY 200 COMPANIES")
        print("-" * 70)
        nifty200 = get_nifty200_companies()
        if nifty200:
            print(f"   Symbols: {', '.join(nifty200[:10])}...")
            export_to_json(nifty200, 'nifty200_companies.json')
            export_to_csv(nifty200, 'nifty200_companies.csv')
        print()
        
        # 4. Fetch all NSE companies
        print("4️⃣  ALL NSE EQUITY COMPANIES")
        print("-" * 70)
        all_nse = get_all_nse_companies()
        if not all_nse.empty:
            print(f"   First 10 companies:")
            print(all_nse.head(10)[['tradingsymbol', 'name']].to_string(index=False))
            export_to_json(all_nse, 'all_nse_companies.json')
            export_to_csv(all_nse, 'all_nse_companies.csv')
        print()
        
        # Summary
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"✅ Nifty 50:  {len(nifty50)} companies")
        print(f"✅ Nifty 100: {len(nifty100)} companies")
        print(f"✅ Nifty 200: {len(nifty200)} companies")
        print(f"✅ All NSE:   {len(all_nse)} companies")
        print()
        print("📁 FILES GENERATED:")
        print("   • nifty50_companies.json/csv")
        print("   • nifty100_companies.json/csv")
        print("   • nifty200_companies.json/csv")
        print("   • all_nse_companies.json/csv")
        print()
        print("=" * 70)

