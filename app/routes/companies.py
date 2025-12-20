"""
Company List API Routes

Provides endpoints to fetch Indian stock market company lists:
- Nifty 50, Nifty 100, Nifty 200
- All NSE equity companies
- Custom company search
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

# Add parent directory to path to import companies module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from companies import (
        get_nifty50_companies,
        get_nifty100_companies,
        get_nifty200_companies,
        get_all_nse_companies
    )
except ImportError:
    # Try importing from app.companies
    from app.companies import (
        get_nifty50_companies,
        get_nifty100_companies,
        get_nifty200_companies,
        get_all_nse_companies
    )

router = APIRouter(prefix="/companies", tags=["companies"])


class CompanyListResponse(BaseModel):
    """Response model for company list endpoints"""
    category: str
    companies: List[str]
    count: int
    success: bool = True


class CompanyDetailResponse(BaseModel):
    """Response model for detailed company information"""
    tradingsymbol: str
    name: str
    instrument_token: int
    exchange: str


@router.get("/nifty50", response_model=CompanyListResponse)
async def get_nifty50():
    """
    Get Nifty 50 company list from NSE India API.
    
    Returns:
        CompanyListResponse: List of Nifty 50 companies
    """
    try:
        companies = get_nifty50_companies()
        return CompanyListResponse(
            category="nifty50",
            companies=companies,
            count=len(companies)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Nifty 50: {str(e)}")


@router.get("/nifty100", response_model=CompanyListResponse)
async def get_nifty100():
    """
    Get Nifty 100 company list from NSE India API.
    
    Returns:
        CompanyListResponse: List of Nifty 100 companies
    """
    try:
        companies = get_nifty100_companies()
        return CompanyListResponse(
            category="nifty100",
            companies=companies,
            count=len(companies)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Nifty 100: {str(e)}")


@router.get("/nifty200", response_model=CompanyListResponse)
async def get_nifty200():
    """
    Get Nifty 200 company list from NSE India API.
    
    Returns:
        CompanyListResponse: List of Nifty 200 companies
    """
    try:
        companies = get_nifty200_companies()
        return CompanyListResponse(
            category="nifty200",
            companies=companies,
            count=len(companies)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Nifty 200: {str(e)}")


@router.get("/all", response_model=dict)
async def get_all_lists():
    """
    Get all company lists in a single response.
    
    Returns:
        dict: Dictionary containing all company lists
    """
    try:
        nifty50 = get_nifty50_companies()
        nifty100 = get_nifty100_companies()
        nifty200 = get_nifty200_companies()
        
        return {
            "nifty50": {
                "companies": nifty50,
                "count": len(nifty50)
            },
            "nifty100": {
                "companies": nifty100,
                "count": len(nifty100)
            },
            "nifty200": {
                "companies": nifty200,
                "count": len(nifty200)
            },
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company lists: {str(e)}")


@router.get("/nse/all")
async def get_all_nse():
    """
    Get all NSE equity companies.
    
    Returns:
        dict: List of all NSE equity companies with details
    """
    try:
        print("📊 Fetching all NSE companies...")  # Debug log
        df = get_all_nse_companies()
        
        if df is None or df.empty:
            print("⚠️  No companies found or error fetching")
            # Return empty result instead of error
            return {
                "companies": [],
                "count": 0,
                "success": True,
                "message": "No companies available. Please check Zerodha API credentials."
            }
        
        # Replace NaN/inf values with None for JSON serialization
        df = df.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
        
        # Convert to dict, only include tradingsymbol and name for simplicity
        if 'tradingsymbol' in df.columns and 'name' in df.columns:
            companies = df[['tradingsymbol', 'name']].to_dict('records')
        else:
            companies = df.to_dict('records')
        
        print(f"✅ Fetched {len(companies)} companies")
        
        return {
            "companies": companies,
            "count": len(companies),
            "success": True
        }
    except Exception as e:
        print(f"❌ Error in get_all_nse: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty result with error message instead of raising exception
        return {
            "companies": [],
            "count": 0,
            "success": False,
            "error": str(e),
            "message": "Failed to fetch NSE companies. Using fallback data."
        }


@router.get("/search")
async def search_companies(
    query: str = Query(..., min_length=2, description="Search query (min 2 characters)"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results")
):
    """
    Search for companies across all NSE companies.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    
    Returns:
        dict: Search results with matching companies
    """
    try:
        df = get_all_nse_companies()
        
        if df.empty:
            return {
                "query": query,
                "companies": [],
                "count": 0,
                "success": True
            }
        
        # Search in both symbol and name columns
        query_lower = query.lower()
        mask = (
            df['tradingsymbol'].str.lower().str.contains(query_lower, na=False) |
            df['name'].str.lower().str.contains(query_lower, na=False)
        )
        
        results = df[mask].head(limit)
        companies = results.to_dict('records')
        
        return {
            "query": query,
            "companies": companies,
            "count": len(companies),
            "total_matches": mask.sum(),
            "limited": mask.sum() > limit,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching companies: {str(e)}")


@router.get("/custom/{category}")
async def get_custom_list(category: str):
    """
    Get a custom company list by category name.
    
    Supports: nifty50, nifty100, nifty200, midcap, smallcap
    
    Args:
        category: Category name
    
    Returns:
        CompanyListResponse: List of companies in the category
    """
    category_map = {
        "nifty50": get_nifty50_companies,
        "nifty100": get_nifty100_companies,
        "nifty200": get_nifty200_companies,
    }
    
    if category.lower() not in category_map:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found. Available: {', '.join(category_map.keys())}"
        )
    
    try:
        companies = category_map[category.lower()]()
        return CompanyListResponse(
            category=category,
            companies=companies,
            count=len(companies)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching {category}: {str(e)}")
