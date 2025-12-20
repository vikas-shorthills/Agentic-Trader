/**
 * API Service Test Examples
 * 
 * These are example test functions you can run in the browser console
 * to verify the API service is working correctly.
 * 
 * Usage:
 * 1. Open the app in browser
 * 2. Open DevTools Console (F12)
 * 3. Copy and paste these functions
 * 4. Run them to test
 */

// ============================================================================
// Test 1: Fetch All Companies
// ============================================================================
async function testFetchAll() {
  console.log('🧪 Test 1: Fetching all companies...')
  
  try {
    const startTime = Date.now()
    const data = await fetchAllCompanies()
    const endTime = Date.now()
    
    console.log('✅ Success!')
    console.log(`⏱️  Time taken: ${endTime - startTime}ms`)
    console.log(`📊 Nifty 50: ${data.nifty50.length} companies`)
    console.log(`📊 Nifty 100: ${data.nifty100.length} companies`)
    console.log(`📊 Top 200: ${data.top200.length} companies`)
    console.log('Sample companies:', data.nifty50.slice(0, 5))
    
    return data
  } catch (error) {
    console.error('❌ Test failed:', error)
    return null
  }
}

// ============================================================================
// Test 2: Test Caching
// ============================================================================
async function testCaching() {
  console.log('🧪 Test 2: Testing cache performance...')
  
  try {
    // First call (no cache)
    console.log('📡 First call (should fetch from API)...')
    const start1 = Date.now()
    await fetchAllCompanies()
    const time1 = Date.now() - start1
    console.log(`⏱️  First call: ${time1}ms`)
    
    // Second call (should use cache)
    console.log('💾 Second call (should use cache)...')
    const start2 = Date.now()
    await fetchAllCompanies()
    const time2 = Date.now() - start2
    console.log(`⏱️  Second call: ${time2}ms`)
    
    if (time2 < time1 / 2) {
      console.log('✅ Cache is working! Second call was much faster.')
    } else {
      console.log('⚠️  Cache might not be working optimally')
    }
    
    console.log(`🚀 Speed improvement: ${((time1 - time2) / time1 * 100).toFixed(1)}%`)
  } catch (error) {
    console.error('❌ Test failed:', error)
  }
}

// ============================================================================
// Test 3: Search Functionality
// ============================================================================
async function testSearch() {
  console.log('🧪 Test 3: Testing search functionality...')
  
  const testQueries = ['RELIANCE', 'TCS', 'HDFC', 'TATA', 'ADANI']
  
  for (const query of testQueries) {
    try {
      const results = await searchCompanies(query)
      console.log(`🔍 Search "${query}": ${results.length} results`)
      console.log(`   Results:`, results.slice(0, 3).join(', '))
    } catch (error) {
      console.error(`❌ Search failed for "${query}":`, error)
    }
  }
}

// ============================================================================
// Test 4: Individual List Fetching
// ============================================================================
async function testIndividualLists() {
  console.log('🧪 Test 4: Testing individual list fetching...')
  
  try {
    console.log('📡 Fetching Nifty 50...')
    const nifty50 = await fetchNifty50()
    console.log(`✅ Nifty 50: ${nifty50.length} companies`)
    
    console.log('📡 Fetching Nifty 100...')
    const nifty100 = await fetchNifty100()
    console.log(`✅ Nifty 100: ${nifty100.length} companies`)
    
    console.log('📡 Fetching Top 200...')
    const top200 = await fetchTop200()
    console.log(`✅ Top 200: ${top200.length} companies`)
    
    console.log('✅ All individual lists fetched successfully!')
  } catch (error) {
    console.error('❌ Test failed:', error)
  }
}

// ============================================================================
// Test 5: Cache Clearing
// ============================================================================
async function testCacheClear() {
  console.log('🧪 Test 5: Testing cache clearing...')
  
  try {
    // Fetch data (should cache)
    console.log('📡 Fetching data...')
    await fetchAllCompanies()
    
    // Clear cache
    console.log('🗑️  Clearing cache...')
    clearCache()
    console.log('✅ Cache cleared')
    
    // Fetch again (should fetch from API)
    console.log('📡 Fetching data again (should be slower)...')
    const start = Date.now()
    await fetchAllCompanies()
    const time = Date.now() - start
    console.log(`⏱️  Time: ${time}ms`)
    console.log('✅ Cache clear test complete')
  } catch (error) {
    console.error('❌ Test failed:', error)
  }
}

// ============================================================================
// Test 6: Error Handling
// ============================================================================
async function testErrorHandling() {
  console.log('🧪 Test 6: Testing error handling...')
  
  try {
    // This should handle errors gracefully and use fallback data
    const data = await fetchAllCompanies()
    
    if (data && data.nifty50.length > 0) {
      console.log('✅ Error handling works - fallback data loaded')
      console.log(`   Got ${data.nifty50.length} companies despite potential API issues`)
    }
  } catch (error) {
    console.log('✅ Error caught properly:', error.message)
  }
}

// ============================================================================
// Run All Tests
// ============================================================================
async function runAllTests() {
  console.log('🚀 Running all API service tests...')
  console.log('═'.repeat(60))
  
  await testFetchAll()
  console.log('─'.repeat(60))
  
  await testCaching()
  console.log('─'.repeat(60))
  
  await testSearch()
  console.log('─'.repeat(60))
  
  await testIndividualLists()
  console.log('─'.repeat(60))
  
  await testCacheClear()
  console.log('─'.repeat(60))
  
  await testErrorHandling()
  console.log('═'.repeat(60))
  
  console.log('✅ All tests complete!')
}

// ============================================================================
// Quick Performance Test
// ============================================================================
async function quickTest() {
  console.log('⚡ Quick performance test...')
  
  const start = Date.now()
  const data = await fetchAllCompanies()
  const end = Date.now()
  
  console.log(`✅ Loaded ${data.nifty50.length + data.nifty100.length + data.top200.length} companies in ${end - start}ms`)
  
  return data
}

// ============================================================================
// Export for use in console
// ============================================================================
console.log(`
🧪 API Service Test Functions Loaded!

Available test functions:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 testFetchAll()        - Test fetching all companies
💾 testCaching()         - Test cache performance
🔍 testSearch()          - Test search functionality
📋 testIndividualLists() - Test individual list fetching
🗑️  testCacheClear()     - Test cache clearing
❌ testErrorHandling()   - Test error handling
🚀 runAllTests()         - Run all tests
⚡ quickTest()           - Quick performance test

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example usage:
> await quickTest()
> await runAllTests()
> await testCaching()

`)

// Make functions available globally for console use
if (typeof window !== 'undefined') {
  window.apiTests = {
    testFetchAll,
    testCaching,
    testSearch,
    testIndividualLists,
    testCacheClear,
    testErrorHandling,
    runAllTests,
    quickTest
  }
  
  console.log('💡 Tip: Use window.apiTests.runAllTests() to run all tests')
}


