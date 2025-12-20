"""
Portfolio Analysis API Routes

Provides endpoints for running investment agent analysis on selected companies.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any, AsyncGenerator
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime
import traceback
import json

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class CompanyAnalysisRequest(BaseModel):
    """Request model for portfolio analysis"""
    companies: List[str] = Field(..., description="List of company ticker symbols", min_length=1)
    investment_amount: Optional[float] = Field(None, description="Total investment amount")
    tenure_weeks: Optional[int] = Field(None, description="Investment tenure in weeks")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD format)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD format)")
    analysis_date: Optional[str] = Field(None, description="Analysis date (YYYY-MM-DD format) - deprecated, use start_date/end_date")


class CompanyAnalysisResult(BaseModel):
    """Result for individual company analysis"""
    symbol: str
    status: str  # "success" or "error"
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str


class PortfolioAnalysisResponse(BaseModel):
    """Response model for portfolio analysis"""
    request_id: str
    total_companies: int
    successful: int
    failed: int
    results: List[CompanyAnalysisResult]
    summary: Optional[Dict[str, Any]] = None
    timestamp: str


async def run_invest_agent_for_company(
    symbol: str, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    analysis_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the invest agent for a single company.
    
    Args:
        symbol: Company ticker symbol
        start_date: Start date for analysis (YYYY-MM-DD)
        end_date: End date for analysis (YYYY-MM-DD)
        analysis_date: Single analysis date (deprecated, use start_date/end_date)
        
    Returns:
        Dict containing analysis results
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            from fastapi import Request
            from google.genai import types
            import uuid
            
            # Construct the query
            if start_date and end_date:
                query = f"Analyze {symbol} from {start_date} to {end_date}"
            elif analysis_date:
                query = f"Analyze {symbol} for {analysis_date}"
            else:
                query = f"Analyze {symbol} for today"
            
            print(f"🔍 Starting analysis for {symbol} (attempt {attempt + 1}/{max_retries})...")
            print(f"   Query: {query}")
            
            # Import at runtime to avoid circular dependencies
            from app.application import create_application
            app = create_application()
            
            # Get the ADK Web Server and session service from app state
            adk_web = app.state.adk_web
            session_service = app.state.session_service
            
            # Generate unique IDs for the session
            user_id = "portfolio_analyzer"
            session_id = f"portfolio_{uuid.uuid4().hex[:8]}"
            
            # Create a new session first
            await session_service.create_session(
                user_id=user_id,
                session_id=session_id,
                app_name="invest_agent"
            )
            
            # Get a runner for the invest_agent
            runner = await adk_web.get_runner_async("invest_agent")
            
            # Create the message content
            new_message = types.Content(
                role="user",
                parts=[types.Part(text=query)]
            )
            
            # Collect all results from the async generator
            full_output = []
            event_count = 0
            
            print(f"🔍 Starting event collection for {symbol}...")
            
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                event_count += 1
                event_type = type(event).__name__
                print(f"\n{'='*60}")
                print(f"Event #{event_count}: {event_type}")
                print(f"{'='*60}")
                
                # Print ALL attributes for debugging
                event_attrs = [attr for attr in dir(event) if not attr.startswith('_')]
                print(f"Available attributes: {event_attrs}")
                
                # Try to extract text from various possible structures
                text_found = False
                
                # Method 1: Check for content.parts (Google GenAI structure)
                if hasattr(event, 'content') and event.content:
                    print(f"✓ Has 'content' attribute")
                    if hasattr(event.content, 'parts'):
                        print(f"✓ Content has 'parts': {len(event.content.parts)} parts")
                        for i, part in enumerate(event.content.parts):
                            part_attrs = [attr for attr in dir(part) if not attr.startswith('_')]
                            print(f"  Part {i} attributes: {part_attrs}")
                            if hasattr(part, 'text') and part.text:
                                print(f"  ✅ Found text in part {i}: {part.text[:200]}...")
                                full_output.append(part.text)
                                text_found = True
                    elif hasattr(event.content, 'text'):
                        print(f"✅ Found text in content: {event.content.text[:200]}...")
                        full_output.append(event.content.text)
                        text_found = True
                
                # Method 2: Direct text attribute
                if not text_found and hasattr(event, 'text') and event.text:
                    print(f"✅ Found direct text attribute: {event.text[:200]}...")
                    full_output.append(event.text)
                    text_found = True
                
                # Method 3: Message attribute
                if not text_found and hasattr(event, 'message'):
                    print(f"✓ Has 'message' attribute: {type(event.message)}")
                    if hasattr(event.message, 'content'):
                        print(f"  ✓ Message has 'content'")
                        if hasattr(event.message.content, 'parts'):
                            print(f"  ✓ Message content has 'parts': {len(event.message.content.parts)}")
                            for i, part in enumerate(event.message.content.parts):
                                if hasattr(part, 'text') and part.text:
                                    print(f"  ✅ Found text in message part {i}: {part.text[:200]}...")
                                    full_output.append(part.text)
                                    text_found = True
                        elif hasattr(event.message.content, 'text'):
                            print(f"  ✅ Found text in message.content: {event.message.content.text[:200]}...")
                            full_output.append(event.message.content.text)
                            text_found = True
                    elif hasattr(event.message, 'text'):
                        print(f"  ✅ Found text in message: {event.message.text[:200]}...")
                        full_output.append(event.message.text)
                        text_found = True
                
                # Method 4: Response attribute
                if not text_found and hasattr(event, 'response'):
                    print(f"✓ Has 'response' attribute: {type(event.response)}")
                    if hasattr(event.response, 'text'):
                        print(f"  ✅ Found text in response: {event.response.text[:200]}...")
                        full_output.append(event.response.text)
                        text_found = True
                
                # Method 5: Dict-like access
                if not text_found and isinstance(event, dict):
                    print(f"Event is a dict with keys: {event.keys()}")
                    if 'text' in event:
                        print(f"✅ Found text in dict['text']: {event['text'][:200]}...")
                        full_output.append(event['text'])
                        text_found = True
                    elif 'content' in event:
                        print(f"✅ Found content in dict['content']: {str(event['content'])[:200]}...")
                        full_output.append(str(event['content']))
                        text_found = True
                
                if not text_found:
                    print(f"⚠️ No text found in this event")
                    # Try to print the event itself
                    try:
                        print(f"Event repr: {repr(event)[:500]}")
                    except:
                        print(f"Could not print event repr")
            
            print(f"\n{'='*60}")
            print(f"📊 SUMMARY: {event_count} events processed, {len(full_output)} text outputs collected")
            print(f"{'='*60}\n")
            
            result_text = '\n'.join(full_output) if full_output else "No message in response"
            
            if not full_output:
                print(f"⚠️ WARNING: No text output was captured from {event_count} events")
            else:
                print(f"✅ Successfully collected {len(full_output)} text segments")
            
            print(f"✅ Completed analysis for {symbol}")
            
            # Parse the agent response
            return {
                "symbol": symbol,
                "status": "error" if not full_output else "success",
                "analysis": {
                    "raw_output": result_text,
                    "query": query,
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except ValueError as e:
            if "No message in response" in str(e):
                print(f"⚠️ LiteLLM returned empty response (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"   Retrying in 2 seconds...")
                    await asyncio.sleep(2)
                    continue
                else:
                    print(f"❌ All retries exhausted for {symbol}")
                    return {
                        "symbol": symbol,
                        "status": "error",
                        "error": "LiteLLM proxy returned empty response after 3 attempts. This may indicate an API quota issue or model configuration problem.",
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                raise
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")
            traceback.print_exc()
            return {
                "symbol": symbol,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Should never reach here
    return {
        "symbol": symbol,
        "status": "error",
        "error": "Unexpected error: max retries exceeded",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/analyze-stream")
async def analyze_portfolio_stream(request: CompanyAnalysisRequest):
    """
    Analyze multiple companies using the invest agent with streaming results.
    
    Returns Server-Sent Events (SSE) with progress updates and results as they complete.
    
    Args:
        request: CompanyAnalysisRequest containing companies and parameters
        
    Returns:
        StreamingResponse with SSE events
    """
    
    async def generate_events() -> AsyncGenerator[str, None]:
        """Generate SSE events for portfolio analysis"""
        try:
            request_id = f"PA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'request_id': request_id, 'total_companies': len(request.companies)})}\n\n"
            
            results = []
            successful = 0
            failed = 0
            
            # Analyze each company and stream results
            for idx, symbol in enumerate(request.companies, 1):
                # Send progress event
                yield f"data: {json.dumps({'type': 'progress', 'current': idx, 'total': len(request.companies), 'symbol': symbol, 'status': 'analyzing'})}\n\n"
                
                # Run analysis with date parameters
                result = await run_invest_agent_for_company(
                    symbol, 
                    start_date=request.start_date,
                    end_date=request.end_date,
                    analysis_date=request.analysis_date
                )
                results.append(result)
                
                if result['status'] == 'success':
                    successful += 1
                else:
                    failed += 1
                
                # Send result event
                yield f"data: {json.dumps({'type': 'result', 'result': result, 'completed': idx, 'total': len(request.companies)})}\n\n"
            
            # Send completion event
            summary = {
                'request_id': request_id,
                'total_companies': len(request.companies),
                'successful_analyses': successful,
                'failed_analyses': failed,
                'successful': successful,
                'failed': failed,
                'investment_amount': request.investment_amount,
                'tenure_weeks': request.tenure_weeks,
                'start_date': request.start_date,
                'end_date': request.end_date,
                'analysis_date': request.analysis_date or datetime.now().strftime('%Y-%m-%d'),
            }
            
            yield f"data: {json.dumps({'type': 'complete', 'summary': summary, 'successful': successful, 'failed': failed})}\n\n"
            
        except Exception as e:
            print(f"❌ Streaming error: {str(e)}")
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.post("/analyze", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(request: CompanyAnalysisRequest):
    """
    Analyze multiple companies using the invest agent.
    
    This endpoint:
    1. Receives a list of company symbols
    2. Runs the invest agent for each company
    3. Returns comprehensive analysis results
    
    Args:
        request: CompanyAnalysisRequest containing companies and parameters
        
    Returns:
        PortfolioAnalysisResponse with analysis results for all companies
    """
    try:
        print(f"\n{'='*60}")
        print(f"📊 PORTFOLIO ANALYSIS REQUEST")
        print(f"{'='*60}")
        print(f"Companies: {request.companies}")
        print(f"Investment Amount: ${request.investment_amount}")
        print(f"Tenure: {request.tenure_weeks} weeks")
        print(f"{'='*60}\n")
        
        # Generate request ID
        request_id = f"PA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Run analysis for each company
        results = []
        for symbol in request.companies:
            result = await run_invest_agent_for_company(symbol, request.analysis_date)
            results.append(CompanyAnalysisResult(**result))
        
        # Calculate summary statistics
        successful = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "error")
        
        # Generate summary
        summary = {
            "request_id": request_id,
            "total_companies": len(request.companies),
            "successful_analyses": successful,
            "failed_analyses": failed,
            "investment_amount": request.investment_amount,
            "tenure_weeks": request.tenure_weeks,
            "analysis_date": request.analysis_date or datetime.now().strftime('%Y-%m-%d'),
        }
        
        response = PortfolioAnalysisResponse(
            request_id=request_id,
            total_companies=len(request.companies),
            successful=successful,
            failed=failed,
            results=results,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )
        
        print(f"\n{'='*60}")
        print(f"✅ PORTFOLIO ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Request ID: {request_id}")
        print(f"Successful: {successful}/{len(request.companies)}")
        print(f"Failed: {failed}/{len(request.companies)}")
        print(f"{'='*60}\n")
        
        return response
        
    except Exception as e:
        print(f"❌ Portfolio analysis error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio analysis failed: {str(e)}"
        )


@router.post("/analyze-single")
async def analyze_single_company(
    symbol: str,
    analysis_date: Optional[str] = None
):
    """
    Analyze a single company using the invest agent.
    
    Args:
        symbol: Company ticker symbol
        analysis_date: Optional analysis date (YYYY-MM-DD)
        
    Returns:
        Dict with analysis results
    """
    try:
        print(f"\n🔍 Analyzing single company: {symbol}")
        result = await run_invest_agent_for_company(symbol, analysis_date)
        return result
        
    except Exception as e:
        print(f"❌ Error analyzing {symbol}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed for {symbol}: {str(e)}"
        )


@router.get("/status/{request_id}")
async def get_analysis_status(request_id: str):
    """
    Get the status of a portfolio analysis request.
    
    Note: This is a placeholder. In production, you would store
    analysis results in a database and retrieve them here.
    
    Args:
        request_id: The request ID from a previous analysis
        
    Returns:
        Dict with status information
    """
    # TODO: Implement database storage and retrieval
    return {
        "request_id": request_id,
        "status": "completed",
        "message": "Status tracking not yet implemented. Results are returned synchronously."
    }


