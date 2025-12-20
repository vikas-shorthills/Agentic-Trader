/**
 * API Service Module
 * 
 * This module provides functions to fetch company data from backend API
 */

// API base URL - can be configured via environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// Cache for company data to avoid repeated API calls
const cache = {
  nifty50: null,
  nifty100: null,
  nifty200: null,
  allNSE: null,
  timestamp: null
}

const CACHE_DURATION = 1000 * 60 * 60 // 1 hour

/**
 * Check if cache is still valid
 */
const isCacheValid = () => {
  if (!cache.timestamp) return false
  return Date.now() - cache.timestamp < CACHE_DURATION
}

/**
 * Fetch Nifty 50 companies from backend API
 */
export const fetchNifty50 = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/companies/nifty50`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    return data.companies || []
  } catch (error) {
    console.warn('Backend API failed for Nifty 50, using fallback:', error)
    
    // Fallback data
    return [
      'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
      'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
      'AXISBANK', 'LT', 'ASIANPAINT', 'BAJFINANCE', 'MARUTI',
      'HCLTECH', 'M&M', 'TITAN', 'WIPRO', 'ULTRACEMCO',
      'NESTLEIND', 'SUNPHARMA', 'POWERGRID', 'TECHM', 'TATASTEEL',
      'INDUSINDBK', 'ADANIPORTS', 'BAJAJFINSV', 'NTPC', 'JSWSTEEL',
      'GRASIM', 'COALINDIA', 'TATACONSUM', 'CIPLA', 'HEROMOTOCO',
      'EICHERMOT', 'BRITANNIA', 'ONGC', 'UPL', 'SHREECEM',
      'DIVISLAB', 'SBILIFE', 'BAJAJ-AUTO', 'HINDALCO', 'ADANIENT',
      'APOLLOHOSP', 'IOC', 'DRREDDY', 'TATAMOTORS', 'BPCL'
    ]
  }
}

/**
 * Fetch Nifty 100 companies from backend API
 */
export const fetchNifty100 = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/companies/nifty100`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    return data.companies || []
  } catch (error) {
    console.warn('Backend API failed for Nifty 100, using fallback:', error)
    
    // Fallback: Nifty 50 + additional companies
    const nifty50 = await fetchNifty50()
    const additional = [
      'ADANIGREEN', 'ADANITRANS', 'AMBUJACEM', 'AUROPHARMA', 'BERGEPAINT',
      'BIOCON', 'BOSCHLTD', 'ZYDUSLIFE', 'COLPAL', 'DABUR',
      'DLF', 'DIVISLAB', 'EICHERMOT', 'GAIL', 'GODREJCP',
      'HAVELLS', 'HDFCLIFE', 'HINDALCO', 'ICICIGI', 'ICICIPRULI',
      'IGL', 'INDIGO', 'JINDALSTEL', 'LUPIN', 'MRF',
      'MOTHERSON', 'MUTHOOTFIN', 'NMDC', 'OIL', 'PETRONET',
      'PIDILITIND', 'PIRAMALENT', 'SBICARD', 'SIEMENS', 'TATAPOWER',
      'TORNTPHARM', 'TVSMOTOR', 'VEDL', 'VOLTAS', 'ZOMATO',
      'PAYTM', 'NYKAA', 'POLICYBZR', 'LICI', 'PNB',
      'BANKBARODA', 'CANBK', 'UNIONBANK', 'INDIANB', 'CENTRALBK'
    ]
    
    return [...nifty50, ...additional]
  }
}

/**
 * Fetch Nifty 200 companies from backend API
 */
export const fetchTop200 = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/companies/nifty200`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    return data.companies || []
  } catch (error) {
    console.warn('Backend API failed for Nifty 200, using fallback:', error)
    
    // Fallback: Nifty 100 + additional companies
    const nifty100 = await fetchNifty100()
    const additional = [
      'ABCAPITAL', 'ALKEM', 'ASHOKLEY', 'ATUL', 'BALKRISIND',
      'BANDHANBNK', 'BEL', 'BHARATFORG', 'BPCL', 'CAMS',
      'CHOLAFIN', 'COFORGE', 'CONCOR', 'CROMPTON', 'CUMMINSIND',
      'DEEPAKNTR', 'DIXON', 'ENDURANCE', 'EXIDEIND', 'FEDERALBNK',
      'FORTIS', 'GLANDPHARMA', 'GMRINFRA', 'GODREJPROP', 'GUJGAS',
      'HONAUT', 'IDBI', 'IDFCFIRSTB', 'INDHOTEL', 'IOC',
      'NAUKRI', 'JSWENERGY', 'JUBLFOOD', 'KEIIND', 'LTIM',
      'LTTS', 'LAURUSLABS', 'LEMONTREE', 'LICHSGFIN', 'MARICO',
      'MFSL', 'MPHASIS', 'NAVINFLUOR', 'OBEROIRLTY', 'OFSS',
      'PAGEIND', 'PERSISTENT', 'POLYCAB', 'PRESTIGE', 'RAJESHEXPO'
    ]
    
    return [...nifty100, ...additional]
  }
}

/**
 * Fetch all company lists with caching
 */
export const fetchAllCompanies = async () => {
  // Return cached data if valid
  if (isCacheValid() && cache.nifty50 && cache.nifty100 && cache.top200) {
    return {
      nifty50: cache.nifty50,
      nifty100: cache.nifty100,
      top200: cache.top200
    }
  }

  try {
    // Try to fetch all lists from backend in a single request
    const response = await fetch(`${API_BASE_URL}/companies/all`)
    
    if (response.ok) {
      const data = await response.json()
      
      cache.nifty50 = data.nifty50?.companies || []
      cache.nifty100 = data.nifty100?.companies || []
      cache.top200 = data.nifty200?.companies || []
      cache.timestamp = Date.now()
      
      return {
        nifty50: cache.nifty50,
        nifty100: cache.nifty100,
        top200: cache.top200
      }
    }
  } catch (error) {
    console.warn('Backend /all endpoint failed, fetching individually:', error)
  }

  // Fallback: Fetch lists individually
  try {
    const [nifty50, nifty100, top200] = await Promise.all([
      fetchNifty50(),
      fetchNifty100(),
      fetchTop200()
    ])

    // Update cache
    cache.nifty50 = nifty50
    cache.nifty100 = nifty100
    cache.top200 = top200
    cache.timestamp = Date.now()

    return { nifty50, nifty100, top200 }
  } catch (error) {
    console.error('Error fetching company lists:', error)
    throw new Error('Failed to fetch company data. Please try again later.')
  }
}

/**
 * Fetch all NSE companies with details
 */
export const fetchAllNSECompanies = async () => {
  // Check cache
  if (isCacheValid() && cache.allNSE) {
    return cache.allNSE
  }

  try {
    const response = await fetch(`${API_BASE_URL}/companies/nse/all`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    cache.allNSE = data.companies || []
    cache.timestamp = Date.now()
    
    return cache.allNSE
  } catch (error) {
    console.error('Error fetching all NSE companies:', error)
    throw error
  }
}

/**
 * Search companies across all lists
 */
export const searchCompanies = async (query, limit = 50) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/companies/search?query=${encodeURIComponent(query)}&limit=${limit}`
    )
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    return data.companies || []
  } catch (error) {
    console.error('Error searching companies:', error)
    
    // Fallback: search in cached data
    const { nifty50, nifty100, top200 } = await fetchAllCompanies()
    const allCompanies = [...new Set([...nifty50, ...nifty100, ...top200])]
    
    const queryLower = query.toLowerCase()
    return allCompanies
      .filter(company => company.toLowerCase().includes(queryLower))
      .slice(0, limit)
  }
}

/**
 * Clear cache (useful for manual refresh)
 */
export const clearCache = () => {
  cache.nifty50 = null
  cache.nifty100 = null
  cache.top200 = null
  cache.allNSE = null
  cache.timestamp = null
}

/**
 * Analyze portfolio with streaming results (Server-Sent Events)
 * 
 * @param {Object} params - Analysis parameters
 * @param {Array<string>} params.companies - List of company ticker symbols
 * @param {number} [params.investment_amount] - Total investment amount
 * @param {number} [params.tenure_weeks] - Investment tenure in weeks
 * @param {string} [params.start_date] - Start date (YYYY-MM-DD)
 * @param {string} [params.end_date] - End date (YYYY-MM-DD)
 * @param {Function} [params.onProgress] - Callback for progress updates
 * @param {Function} [params.onResult] - Callback for each company result
 * @returns {Promise<Object>} Final analysis summary with all results
 */
export const analyzePortfolioStream = async ({ 
  companies, 
  investment_amount, 
  tenure_weeks, 
  start_date,
  end_date,
  onProgress,
  onResult
}) => {
  console.log('📊 Starting streaming portfolio analysis:', { companies, investment_amount, tenure_weeks, start_date, end_date })
  
  try {
    const response = await fetch(`${API_BASE_URL}/portfolio/analyze-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        companies,
        investment_amount,
        tenure_weeks,
        start_date,
        end_date
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    // Read the stream
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    const results = []
    let summary = null

    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true })
      
      // Process complete SSE messages (separated by \n\n)
      const messages = buffer.split('\n\n')
      buffer = messages.pop() || '' // Keep incomplete message in buffer
      
      for (const message of messages) {
        if (!message.trim()) continue
        
        // Parse SSE format: "data: {...}"
        const dataMatch = message.match(/^data: (.+)$/m)
        if (!dataMatch) continue
        
        try {
          const event = JSON.parse(dataMatch[1])
          console.log('📨 SSE Event:', event.type, event)
          
          switch (event.type) {
            case 'start':
              console.log(`🚀 Starting analysis for ${event.total_companies} companies`)
              break
              
            case 'progress':
              console.log(`⏳ Analyzing ${event.symbol} (${event.current}/${event.total})`)
              if (onProgress) {
                onProgress(event.current, event.total, event.symbol)
              }
              break
              
            case 'result':
              console.log(`✅ Completed ${event.result.symbol}`)
              results.push(event.result)
              if (onResult) {
                onResult(event.result, event.completed, event.total)
              }
              break
              
            case 'complete':
              console.log('🎉 Analysis complete!', event.summary)
              summary = event.summary
              break
              
            case 'error':
              console.error('❌ Streaming error:', event.error)
              throw new Error(event.error)
          }
        } catch (parseError) {
          console.error('Failed to parse SSE event:', parseError, dataMatch[1])
        }
      }
    }

    console.log('✅ Stream completed:', { results: results.length, summary })
    
    return {
      ...summary,
      results,
      success: true
    }
    
  } catch (error) {
    console.error('❌ Streaming portfolio analysis failed:', error)
    throw error
  }
}


/**
 * Analyze portfolio of companies using AI invest agent
 * 
 * @param {Object} params - Analysis parameters
 * @param {Array<string>} params.companies - List of company ticker symbols
 * @param {number} [params.investment_amount] - Total investment amount
 * @param {number} [params.tenure_weeks] - Investment tenure in weeks
 * @param {string} [params.analysis_date] - Analysis date (YYYY-MM-DD)
 * @returns {Promise<Object>} Portfolio analysis results
 */
export const analyzePortfolio = async ({ companies, investment_amount, tenure_weeks, analysis_date }) => {
  try {
    console.log('📊 Sending portfolio analysis request:', { companies, investment_amount, tenure_weeks })
    
    // Create AbortController with timeout (15 minutes for multiple companies)
    // Each company takes ~6 minutes, so allow plenty of time
    const timeoutMs = 15 * 60 * 1000 // 15 minutes
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs)
    
    const response = await fetch(`${API_BASE_URL}/portfolio/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        companies,
        investment_amount,
        tenure_weeks,
        analysis_date
      }),
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    console.log('✅ Portfolio analysis complete:', data)
    
    return data
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('❌ Request timeout - analysis took too long')
      throw new Error('Analysis timeout: Request took longer than 15 minutes. Please try with fewer companies.')
    }
    console.error('❌ Portfolio analysis failed:', error)
    throw error
  }
}

/**
 * Analyze a single company
 * 
 * @param {string} symbol - Company ticker symbol
 * @param {string} [analysis_date] - Analysis date (YYYY-MM-DD)
 * @returns {Promise<Object>} Company analysis result
 */
export const analyzeSingleCompany = async (symbol, analysis_date = null) => {
  try {
    console.log(`🔍 Analyzing single company: ${symbol}`)
    
    const url = new URL(`${API_BASE_URL}/portfolio/analyze-single`)
    url.searchParams.append('symbol', symbol)
    if (analysis_date) {
      url.searchParams.append('analysis_date', analysis_date)
    }

    const response = await fetch(url, {
      method: 'POST'
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    console.log(`✅ Analysis complete for ${symbol}:`, data)
    
    return data
  } catch (error) {
    console.error(`❌ Analysis failed for ${symbol}:`, error)
    throw error
  }
}

/**
 * Get status of a portfolio analysis request
 * 
 * @param {string} request_id - Request ID from previous analysis
 * @returns {Promise<Object>} Analysis status
 */
export const getAnalysisStatus = async (request_id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/portfolio/status/${request_id}`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching analysis status:', error)
    throw error
  }
}
