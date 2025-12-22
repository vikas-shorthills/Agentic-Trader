"""
Kite Connect Instruments Routes

Handles fetching and caching of instruments from Kite Connect:
- Fetches gzipped CSV dump of all instruments across all exchanges
- Caches the data locally with timestamp
- Provides endpoints to retrieve instruments by exchange, segment, or symbol
- Implements recommended daily refresh pattern (08:30 AM)
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import requests
import gzip
import csv
import io
import json
from pathlib import Path

router = APIRouter(prefix="/instruments", tags=["instruments"])

# Configuration
CACHE_DIR = Path("/home/shtlp_0170/Videos/hackthon/Agentic-Trader/cache")
CACHE_FILE = CACHE_DIR / "instruments.csv.gz"  # Store as gzipped CSV
CACHE_METADATA_FILE = CACHE_DIR / "instruments_metadata.json"
KITE_INSTRUMENTS_URL = "https://api.kite.trade/instruments"
CACHE_DURATION_HOURS = 24  # Recommended: fetch once daily

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class InstrumentModel(BaseModel):
    """Model for a single instrument"""
    instrument_token: str
    exchange_token: str
    tradingsymbol: str
    name: Optional[str] = None
    last_price: Optional[float] = None
    expiry: Optional[str] = None
    strike: Optional[float] = None
    tick_size: Optional[float] = None
    lot_size: Optional[int] = None
    instrument_type: Optional[str] = None
    segment: Optional[str] = None
    exchange: Optional[str] = None


class InstrumentsResponse(BaseModel):
    """Response model for instruments list"""
    success: bool
    count: int
    instruments: List[Dict[str, Any]]
    cached_at: Optional[str] = None
    cache_age_hours: Optional[float] = None


class CacheMetadata(BaseModel):
    """Metadata about the cached instruments"""
    cached_at: str
    total_instruments: int
    exchanges: List[str]
    segments: List[str]


def get_access_token() -> Optional[str]:
    """Get access token from kite_auth session"""
    from app.routes.kite_auth import get_current_access_token
    return get_current_access_token()


def is_cache_valid() -> bool:
    """
    Check if the cached data is still valid.
    
    Returns:
        bool: True if cache exists and is less than CACHE_DURATION_HOURS old
    """
    if not CACHE_FILE.exists() or not CACHE_METADATA_FILE.exists():
        return False
    
    try:
        with open(CACHE_METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        
        cached_at = datetime.fromisoformat(metadata['cached_at'])
        age = datetime.now() - cached_at
        
        return age.total_seconds() < (CACHE_DURATION_HOURS * 3600)
    except Exception as e:
        print(f"Error checking cache validity: {e}")
        return False


def fetch_instruments_from_kite(access_token: str) -> tuple[List[Dict[str, Any]], bytes]:
    """
    Fetch instruments from Kite API.
    
    Args:
        access_token: Kite Connect access token
        
    Returns:
        Tuple of (parsed instruments list, raw gzipped content)
        
    Raises:
        HTTPException: If API request fails
    """
    try:
        headers = {
            "X-Kite-Version": "3",
            "Authorization": f"token {os.getenv('ZERODHA_API_KEY')}:{access_token}"
        }
        
        print(f"📡 Fetching instruments from Kite API...")
        response = requests.get(KITE_INSTRUMENTS_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save raw content for caching
        raw_content = response.content
        
        # Try to decompress if it's gzipped, otherwise gzip it
        try:
            decompressed_data = gzip.decompress(raw_content)
            csv_content = decompressed_data.decode('utf-8')
            gzipped_content = raw_content  # Already gzipped
            print("✅ Response is gzipped CSV - using as-is")
        except gzip.BadGzipFile:
            # Not gzipped, use content directly and gzip it for storage
            print("⚠️  Response is not gzipped, compressing for storage...")
            csv_content = response.text
            gzipped_content = gzip.compress(csv_content.encode('utf-8'))
            print("✅ Successfully compressed plain CSV to .gz format")
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        instruments = []
        
        for row in csv_reader:
            # Convert numeric fields
            instrument = {
                'instrument_token': row.get('instrument_token', ''),
                'exchange_token': row.get('exchange_token', ''),
                'tradingsymbol': row.get('tradingsymbol', ''),
                'name': row.get('name', ''),
                'last_price': float(row.get('last_price', 0)) if row.get('last_price') else None,
                'expiry': row.get('expiry', ''),
                'strike': float(row.get('strike', 0)) if row.get('strike') else None,
                'tick_size': float(row.get('tick_size', 0)) if row.get('tick_size') else None,
                'lot_size': int(row.get('lot_size', 0)) if row.get('lot_size') else None,
                'instrument_type': row.get('instrument_type', ''),
                'segment': row.get('segment', ''),
                'exchange': row.get('exchange', ''),
            }
            instruments.append(instrument)
        
        print(f"✅ Fetched {len(instruments)} instruments from Kite")
        return instruments, gzipped_content
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching instruments from Kite: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch instruments: {str(e)}")


def cache_instruments(instruments: List[Dict[str, Any]], gzipped_content: bytes) -> None:
    """
    Cache instruments to local file as gzipped CSV.
    
    Args:
        instruments: List of instrument dictionaries (for metadata)
        gzipped_content: Raw gzipped CSV content to save
    """
    try:
        # Save raw gzipped CSV file
        with open(CACHE_FILE, 'wb') as f:
            f.write(gzipped_content)
        
        # Extract unique exchanges and segments from parsed data
        exchanges = list(set(inst['exchange'] for inst in instruments if inst.get('exchange')))
        segments = list(set(inst['segment'] for inst in instruments if inst.get('segment')))
        
        # Save metadata
        metadata = {
            'cached_at': datetime.now().isoformat(),
            'total_instruments': len(instruments),
            'exchanges': sorted(exchanges),
            'segments': sorted(segments),
            'file_format': 'csv.gz',
            'file_size_bytes': len(gzipped_content)
        }
        
        with open(CACHE_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        file_size_mb = len(gzipped_content) / (1024 * 1024)
        print(f"✅ Cached {len(instruments)} instruments to {CACHE_FILE} ({file_size_mb:.2f} MB)")
        
    except Exception as e:
        print(f"❌ Error caching instruments: {e}")


def load_cached_instruments() -> Optional[List[Dict[str, Any]]]:
    """
    Load instruments from cached gzipped CSV file.
    
    Returns:
        List of instrument dictionaries or None if cache doesn't exist
    """
    try:
        if CACHE_FILE.exists():
            # Read gzipped CSV file
            with open(CACHE_FILE, 'rb') as f:
                gzipped_content = f.read()
            
            # Decompress
            decompressed_data = gzip.decompress(gzipped_content)
            csv_content = decompressed_data.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            instruments = []
            
            for row in csv_reader:
                instrument = {
                    'instrument_token': row.get('instrument_token', ''),
                    'exchange_token': row.get('exchange_token', ''),
                    'tradingsymbol': row.get('tradingsymbol', ''),
                    'name': row.get('name', ''),
                    'last_price': float(row.get('last_price', 0)) if row.get('last_price') else None,
                    'expiry': row.get('expiry', ''),
                    'strike': float(row.get('strike', 0)) if row.get('strike') else None,
                    'tick_size': float(row.get('tick_size', 0)) if row.get('tick_size') else None,
                    'lot_size': int(row.get('lot_size', 0)) if row.get('lot_size') else None,
                    'instrument_type': row.get('instrument_type', ''),
                    'segment': row.get('segment', ''),
                    'exchange': row.get('exchange', ''),
                }
                instruments.append(instrument)
            
            print(f"✅ Loaded {len(instruments)} instruments from cache")
            return instruments
        return None
    except Exception as e:
        print(f"❌ Error loading cached instruments: {e}")
        return None


def get_cache_metadata() -> Optional[Dict[str, Any]]:
    """
    Get cache metadata.
    
    Returns:
        Metadata dictionary or None if not available
    """
    try:
        if CACHE_METADATA_FILE.exists():
            with open(CACHE_METADATA_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"❌ Error loading cache metadata: {e}")
        return None


@router.get("/all", response_model=InstrumentsResponse)
async def get_all_instruments(
    force_refresh: bool = Query(False, description="Force refresh from Kite API")
):
    """
    Get all instruments. Uses cached data if available and valid.
    
    Args:
        force_refresh: Force fetch from Kite API even if cache is valid
        
    Returns:
        InstrumentsResponse: All instruments with metadata
    """
    try:
        # Check if we need to fetch fresh data
        should_fetch = force_refresh or not is_cache_valid()
        
        if should_fetch:
            # Get access token
            access_token = get_access_token()
            if not access_token:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated with Kite. Please login first."
                )
            
            # Fetch from Kite API (returns both parsed data and raw gzipped content)
            instruments, gzipped_content = fetch_instruments_from_kite(access_token)
            
            # Cache the data
            cache_instruments(instruments, gzipped_content)
        else:
            # Load from cache
            instruments = load_cached_instruments()
            if not instruments:
                raise HTTPException(
                    status_code=500,
                    detail="Cache invalid but failed to load. Try force_refresh=true"
                )
        
        # Get metadata
        metadata = get_cache_metadata()
        cache_age = None
        cached_at = None
        
        if metadata:
            cached_at = metadata['cached_at']
            cached_time = datetime.fromisoformat(cached_at)
            cache_age = (datetime.now() - cached_time).total_seconds() / 3600
        
        return InstrumentsResponse(
            success=True,
            count=len(instruments),
            instruments=instruments,
            cached_at=cached_at,
            cache_age_hours=round(cache_age, 2) if cache_age else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_all_instruments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_instruments(
    query: str = Query(..., description="Search query for tradingsymbol or name"),
    exchange: Optional[str] = Query(None, description="Filter by exchange (NSE, BSE, NFO, etc.)"),
    instrument_type: Optional[str] = Query(None, description="Filter by instrument type (EQ, FUT, CE, PE)"),
    limit: int = Query(100, description="Maximum number of results")
):
    """
    Search instruments by tradingsymbol or name.
    
    Args:
        query: Search string
        exchange: Optional exchange filter
        instrument_type: Optional instrument type filter
        limit: Maximum results to return
        
    Returns:
        Filtered list of instruments
    """
    try:
        # Load instruments
        instruments = load_cached_instruments()
        
        if not instruments:
            raise HTTPException(
                status_code=404,
                detail="No cached instruments. Call /instruments/all first to fetch data."
            )
        
        # Filter instruments
        query_upper = query.upper()
        filtered = []
        
        for inst in instruments:
            # Text search
            matches_query = (
                query_upper in inst.get('tradingsymbol', '').upper() or
                query_upper in inst.get('name', '').upper()
            )
            
            # Exchange filter
            matches_exchange = (
                exchange is None or 
                inst.get('exchange', '').upper() == exchange.upper()
            )
            
            # Instrument type filter
            matches_type = (
                instrument_type is None or
                inst.get('instrument_type', '').upper() == instrument_type.upper()
            )
            
            if matches_query and matches_exchange and matches_type:
                filtered.append(inst)
                
                if len(filtered) >= limit:
                    break
        
        return {
            "success": True,
            "count": len(filtered),
            "instruments": filtered,
            "query": query,
            "filters": {
                "exchange": exchange,
                "instrument_type": instrument_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in search_instruments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata")
async def get_metadata():
    """
    Get metadata about cached instruments.
    
    Returns:
        Cache metadata including count, exchanges, segments, and cache age
    """
    try:
        metadata = get_cache_metadata()
        
        if not metadata:
            return {
                "success": False,
                "message": "No cached data available. Call /instruments/all first."
            }
        
        cached_at = datetime.fromisoformat(metadata['cached_at'])
        age_hours = (datetime.now() - cached_at).total_seconds() / 3600
        is_valid = age_hours < CACHE_DURATION_HOURS
        
        return {
            "success": True,
            "cached_at": metadata['cached_at'],
            "cache_age_hours": round(age_hours, 2),
            "is_cache_valid": is_valid,
            "total_instruments": metadata['total_instruments'],
            "exchanges": metadata['exchanges'],
            "segments": metadata['segments'],
            "cache_duration_hours": CACHE_DURATION_HOURS
        }
        
    except Exception as e:
        print(f"❌ Error in get_metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache")
async def clear_cache():
    """
    Clear cached instruments data.
    
    Returns:
        Success message
    """
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        if CACHE_METADATA_FILE.exists():
            CACHE_METADATA_FILE.unlink()
        
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
        
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/jobs")
async def get_scheduled_jobs_info():
    """
    Get information about scheduled jobs.
    
    Returns:
        List of scheduled jobs with their next run times
    """
    try:
        from app.services.scheduler_service import get_scheduled_jobs
        jobs = get_scheduled_jobs()
        
        return {
            "success": True,
            "jobs": jobs
        }
        
    except Exception as e:
        print(f"❌ Error getting scheduled jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/trigger")
async def trigger_fetch_now():
    """
    Manually trigger the instrument fetch job immediately.
    
    Returns:
        Result of the fetch operation
    """
    try:
        from app.services.scheduler_service import trigger_instrument_fetch_now
        result = await trigger_instrument_fetch_now()
        
        return result
        
    except Exception as e:
        print(f"❌ Error triggering instrument fetch: {e}")
        raise HTTPException(status_code=500, detail=str(e))
