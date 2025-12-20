# Portfolio Analysis API Integration

## Overview
The Portfolio Analysis API allows you to submit companies from the frontend and run investment agent analysis on them.

## Endpoint

### POST `/api/v1/portfolio/analyze`

Analyzes multiple companies using the AI investment agent system.

## Request Format

```javascript
// Example POST request
const response = await fetch('http://localhost:8000/api/v1/portfolio/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    companies: ['AAPL', 'GOOGL', 'MSFT'],  // Required: Array of ticker symbols
    investment_amount: 10000,               // Optional: Total investment amount
    tenure_weeks: 12,                       // Optional: Investment tenure in weeks
    analysis_date: '2025-12-19'            // Optional: Analysis date (YYYY-MM-DD)
  })
});

const data = await response.json();
console.log(data);
```

## Request Body Schema

```typescript
interface CompanyAnalysisRequest {
  companies: string[];          // Required, minimum 1 company
  investment_amount?: number;   // Optional
  tenure_weeks?: number;        // Optional
  analysis_date?: string;       // Optional, format: YYYY-MM-DD
}
```

## Response Format

```typescript
interface PortfolioAnalysisResponse {
  request_id: string;           // Unique ID for this analysis request
  total_companies: number;      // Total number of companies analyzed
  successful: number;           // Number of successful analyses
  failed: number;              // Number of failed analyses
  results: CompanyAnalysisResult[];
  summary: {
    request_id: string;
    total_companies: number;
    successful_analyses: number;
    failed_analyses: number;
    investment_amount?: number;
    tenure_weeks?: number;
    analysis_date: string;
  };
  timestamp: string;           // ISO timestamp
}

interface CompanyAnalysisResult {
  symbol: string;              // Company ticker
  status: 'success' | 'error';
  analysis?: {
    raw_output: string;        // Full agent analysis
    query: string;             // Query sent to agent
  };
  error?: string;              // Error message if failed
  timestamp: string;           // ISO timestamp
}
```

## Example Response

```json
{
  "request_id": "PA-20251219-173000",
  "total_companies": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "symbol": "AAPL",
      "status": "success",
      "analysis": {
        "raw_output": "=== INVESTMENT ANALYSIS: AAPL ===\n\nPHASE 1: ANALYST REPORTS...",
        "query": "Analyze AAPL for today"
      },
      "timestamp": "2025-12-19T17:30:15.123456"
    },
    {
      "symbol": "GOOGL",
      "status": "success",
      "analysis": {
        "raw_output": "=== INVESTMENT ANALYSIS: GOOGL ===...",
        "query": "Analyze GOOGL for today"
      },
      "timestamp": "2025-12-19T17:30:45.789012"
    },
    {
      "symbol": "MSFT",
      "status": "success",
      "analysis": {
        "raw_output": "=== INVESTMENT ANALYSIS: MSFT ===...",
        "query": "Analyze MSFT for today"
      },
      "timestamp": "2025-12-19T17:31:15.345678"
    }
  ],
  "summary": {
    "request_id": "PA-20251219-173000",
    "total_companies": 3,
    "successful_analyses": 3,
    "failed_analyses": 0,
    "investment_amount": 10000,
    "tenure_weeks": 12,
    "analysis_date": "2025-12-19"
  },
  "timestamp": "2025-12-19T17:31:16.000000"
}
```

## React Integration Example

```jsx
import { useState } from 'react';

function PortfolioCalculator() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const calculatePortfolio = async (companies, investmentAmount, tenureWeeks) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/portfolio/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          companies,
          investment_amount: investmentAmount,
          tenure_weeks: tenureWeeks,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      console.log('Portfolio Analysis:', data);
      
      // Process results
      data.results.forEach(result => {
        if (result.status === 'success') {
          console.log(`✅ ${result.symbol}: Analysis complete`);
          // Parse and display result.analysis.raw_output
        } else {
          console.log(`❌ ${result.symbol}: ${result.error}`);
        }
      });
      
    } catch (err) {
      console.error('Portfolio analysis failed:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button 
        onClick={() => calculatePortfolio(
          ['AAPL', 'GOOGL', 'MSFT'], 
          10000, 
          12
        )}
        disabled={loading}
      >
        {loading ? 'Analyzing...' : 'Calculate Portfolio'}
      </button>
      
      {error && <div className="error">{error}</div>}
      
      {results && (
        <div className="results">
          <h3>Analysis Complete!</h3>
          <p>Request ID: {results.request_id}</p>
          <p>Successful: {results.successful} / {results.total_companies}</p>
          
          {results.results.map(result => (
            <div key={result.symbol} className="company-result">
              <h4>{result.symbol}</h4>
              {result.status === 'success' ? (
                <pre>{result.analysis.raw_output}</pre>
              ) : (
                <p className="error">{result.error}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PortfolioCalculator;
```

## Additional Endpoints

### Analyze Single Company
```
POST /api/v1/portfolio/analyze-single?symbol=AAPL&analysis_date=2025-12-19
```

### Check Analysis Status
```
GET /api/v1/portfolio/status/{request_id}
```

## Important Notes

1. **Performance**: Each company analysis takes ~20-30 seconds. For 5 companies, expect ~2-3 minutes total.
2. **Sequential Processing**: Companies are analyzed one at a time to avoid overwhelming the system.
3. **Error Handling**: If one company fails, others will still be processed.
4. **Rate Limiting**: Consider adding a loading indicator and disabling the submit button during analysis.

## Testing with curl

```bash
# Test the endpoint
curl -X POST http://localhost:8000/api/v1/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "companies": ["AAPL", "GOOGL"],
    "investment_amount": 10000,
    "tenure_weeks": 12
  }'
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


