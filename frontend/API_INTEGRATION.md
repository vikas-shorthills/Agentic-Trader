# Frontend API Integration Guide

This document explains how the frontend fetches company data directly from external APIs.

## Overview

The application fetches Indian stock market company lists (Nifty 50, Nifty 100, Top 200) directly from external APIs without going through the backend server.

## API Service

Location: `src/services/api.js`

### Features

1. **Direct External API Calls**: Fetches data from NSE India APIs
2. **Caching**: Implements 1-hour cache to reduce API calls
3. **Fallback Data**: Provides fallback data if external APIs fail
4. **Error Handling**: Graceful error handling with user-friendly messages

### Main Functions

#### `fetchAllCompanies()`
Fetches all three company lists in parallel with caching support.

```javascript
const { nifty50, nifty100, top200 } = await fetchAllCompanies()
```

#### `fetchNifty50()`
Fetches Nifty 50 companies from NSE API with fallback.

```javascript
const nifty50Companies = await fetchNifty50()
```

#### `fetchNifty100()`
Fetches Nifty 100 companies from NSE API with fallback.

```javascript
const nifty100Companies = await fetchNifty100()
```

#### `fetchTop200()`
Fetches Top 200 companies from NSE API with fallback.

```javascript
const top200Companies = await fetchTop200()
```

#### `searchCompanies(query)`
Searches across all company lists.

```javascript
const results = await searchCompanies('Reliance')
```

#### `clearCache()`
Manually clears the cache to force fresh data fetch.

```javascript
clearCache()
```

## External APIs Used

### Primary Source: NSE India API

**Base URL**: `https://www.nseindia.com/api/`

**Endpoints**:
- Nifty 50: `equity-stockIndices?index=NIFTY%2050`
- Nifty 100: `equity-stockIndices?index=NIFTY%20100`
- Nifty 200: `equity-stockIndices?index=NIFTY%20200`

**Note**: These APIs may require CORS handling. The application includes fallback data for cases where CORS blocks the requests.

## CORS Handling

### Issue
Browser security policies (CORS) may block direct API calls to external domains.

### Solutions

1. **Use CORS Proxy** (Development):
   ```javascript
   const CORS_PROXY = 'https://cors-anywhere.herokuapp.com/'
   fetch(CORS_PROXY + 'https://www.nseindia.com/api/...')
   ```

2. **Backend Proxy** (Production):
   Route external API calls through your backend server.

3. **Fallback Data** (Current Implementation):
   The app uses built-in fallback data when external APIs are blocked.

## Usage in Components

### CompanySelectionModal Example

```javascript
import { fetchAllCompanies } from '../../services/api'

const loadCompanyData = async () => {
  setLoading(true)
  try {
    const data = await fetchAllCompanies()
    setCompanyLists({
      nifty50: data.nifty50,
      nifty100: data.nifty100,
      top200: data.top200
    })
  } catch (err) {
    setError('Failed to load company lists')
  } finally {
    setLoading(false)
  }
}
```

## Alternative External APIs

If NSE API doesn't work, you can integrate these alternatives:

### 1. Yahoo Finance API
```javascript
const response = await fetch(
  `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${symbol}`
)
```

### 2. Alpha Vantage
```javascript
const API_KEY = 'your_key'
const response = await fetch(
  `https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=${query}&apikey=${API_KEY}`
)
```

### 3. Finnhub
```javascript
const API_KEY = 'your_key'
const response = await fetch(
  `https://finnhub.io/api/v1/stock/symbol?exchange=NSE&token=${API_KEY}`
)
```

## Testing

### Manual Testing
1. Open the application
2. Click "Add Companies from List"
3. Check browser console for API call logs
4. Verify companies are loaded in the modal

### Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Click "Add Companies from List"
4. Look for API requests to NSE or fallback behavior

## Troubleshooting

### No Companies Loading
- **Check Console**: Look for error messages
- **Check Network Tab**: See if API calls are being made
- **CORS Error**: Expected - fallback data should load automatically

### Slow Loading
- **First Load**: May take time to fetch from external APIs
- **Subsequent Loads**: Should be instant due to caching
- **Clear Cache**: Use `clearCache()` if data seems stale

### Wrong Data
- **Cache Issue**: Clear browser cache or use `clearCache()`
- **API Changes**: External APIs may change format - update parsing logic

## Future Enhancements

1. **Add More Sources**: Integrate multiple APIs for reliability
2. **Real-time Data**: Add WebSocket support for live prices
3. **Company Details**: Fetch additional company information
4. **Smart Caching**: Implement more sophisticated caching strategies
5. **Offline Support**: Use service workers for offline access

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Rate Limiting**: Respect API rate limits with caching
3. **Data Validation**: Always validate external API responses
4. **Error Handling**: Never expose API errors to end users

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_CORS_PROXY=https://cors-anywhere.herokuapp.com
```

Access in code:
```javascript
const API_URL = import.meta.env.VITE_API_BASE_URL
```


