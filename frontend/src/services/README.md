# Services Directory

This directory contains service modules for API communication and data fetching.

## API Service (`api.js`)

The API service provides functions to fetch Indian stock market company data directly from external APIs.

### Quick Start

```javascript
import { fetchAllCompanies, searchCompanies, clearCache } from './services/api'

// Fetch all company lists
const loadData = async () => {
  try {
    const { nifty50, nifty100, top200 } = await fetchAllCompanies()
    console.log('Nifty 50:', nifty50)
    console.log('Nifty 100:', nifty100)
    console.log('Top 200:', top200)
  } catch (error) {
    console.error('Error:', error)
  }
}

// Search for companies
const search = async () => {
  const results = await searchCompanies('RELIANCE')
  console.log('Search results:', results)
}

// Clear cache for fresh data
clearCache()
```

### Features

✅ **Automatic Caching**: 1-hour cache to minimize API calls  
✅ **Fallback Data**: Built-in fallback if external APIs fail  
✅ **Error Handling**: Graceful error handling with detailed messages  
✅ **CORS Ready**: Handles CORS issues with fallback data  
✅ **Parallel Fetching**: Fetches multiple lists simultaneously  

### API Functions

#### Core Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `fetchAllCompanies()` | Fetch all three lists (cached) | `{ nifty50, nifty100, top200 }` |
| `fetchNifty50()` | Fetch Nifty 50 companies | `Array<string>` |
| `fetchNifty100()` | Fetch Nifty 100 companies | `Array<string>` |
| `fetchTop200()` | Fetch Top 200 companies | `Array<string>` |
| `searchCompanies(query)` | Search across all lists | `Array<string>` |
| `clearCache()` | Clear cached data | `void` |

### Data Sources

**Primary**: NSE India API
- `https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050`
- `https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100`
- `https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200`

**Fallback**: Built-in company lists when external APIs are unavailable

### Example: React Component

```jsx
import React, { useState, useEffect } from 'react'
import { fetchAllCompanies } from '../services/api'

function CompanyList() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadCompanies()
  }, [])

  const loadCompanies = async () => {
    try {
      setLoading(true)
      const data = await fetchAllCompanies()
      setCompanies(data.nifty50)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <ul>
      {companies.map(company => (
        <li key={company}>{company}</li>
      ))}
    </ul>
  )
}
```

### Caching Behavior

The service implements automatic caching with a 1-hour duration:

```javascript
const CACHE_DURATION = 1000 * 60 * 60 // 1 hour

// First call: Fetches from API
await fetchAllCompanies() // ~2-3 seconds

// Second call within 1 hour: Returns cached data
await fetchAllCompanies() // Instant

// After 1 hour: Fetches fresh data from API
await fetchAllCompanies() // ~2-3 seconds
```

### Error Handling

The service handles errors gracefully:

```javascript
try {
  const data = await fetchAllCompanies()
  // Use data
} catch (error) {
  // Error contains fallback data
  console.error('API failed, using fallback data')
}
```

### CORS Issues

If you encounter CORS errors:

1. **Development**: The fallback data will load automatically
2. **Production**: Consider:
   - Using a CORS proxy
   - Implementing backend proxy endpoints
   - Using alternative APIs with CORS support

### Performance Tips

1. **Preload Data**: Load company data on app initialization
2. **Cache Wisely**: Use the built-in cache, don't refetch unnecessarily
3. **Lazy Load**: Only fetch data when needed (modal opens, etc.)
4. **Debounce Search**: Implement debouncing for search functionality

### Testing

```javascript
// Test in browser console
import * as api from './services/api'

// Test fetch
api.fetchAllCompanies().then(console.log)

// Test search
api.searchCompanies('TCS').then(console.log)

// Test cache
api.clearCache()
api.fetchAllCompanies() // Should fetch fresh data
```

### Troubleshooting

**Problem**: Companies not loading  
**Solution**: Check browser console for errors, verify network connectivity

**Problem**: Stale data  
**Solution**: Call `clearCache()` to force refresh

**Problem**: CORS errors  
**Solution**: Expected behavior, fallback data will load automatically

**Problem**: Slow loading  
**Solution**: First load is slow, subsequent loads use cache

### Future Enhancements

- [ ] Add WebSocket support for real-time data
- [ ] Integrate multiple data sources for redundancy
- [ ] Add company details fetching
- [ ] Implement intelligent cache invalidation
- [ ] Add offline support with service workers


