import CompanyInput from '../components/home/CompanyInput'
import InvestmentSummary from '../components/home/InvestmentSummary'
import { analyzePortfolioStream } from '../services/api'
import { usePortfolio } from '../contexts/PortfolioContext'

const Home = () => {
  const {
    formData,
    submitted,
    setSubmitted,
    loading,
    setLoading,
    analysisResults,
    setAnalysisResults,
    error,
    setError,
    streamProgress,
    setStreamProgress,
    handleInputChange,
    handleReset
  } = usePortfolio()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setStreamProgress({ current: 0, total: formData.companies.length, symbol: '', results: [] })
    
    try {
      console.log('🚀 Starting streaming portfolio analysis...')
      
      // Call the backend API with streaming
      const results = await analyzePortfolioStream({
        companies: formData.companies,
        investment_amount: parseFloat(formData.amount),
        tenure_weeks: parseInt(formData.tenure),
        start_date: formData.startDate,
        end_date: formData.endDate,
        onProgress: (current, total, symbol) => {
          console.log(`📈 Progress: ${current}/${total} - ${symbol}`)
          setStreamProgress(prev => ({ ...prev, current, total, symbol }))
        },
        onResult: (result, completed, total) => {
          console.log(`✅ Result received: ${result.symbol}`)
          setStreamProgress(prev => ({
            ...prev,
            results: [...prev.results, result],
            current: completed,
            total
          }))
        }
      })
      
      console.log('✅ Portfolio analysis complete:', results)
      
      // Store the final results
      setAnalysisResults(results)
      setSubmitted(true)
      
    } catch (err) {
      console.error('❌ Portfolio analysis error:', err)
      setError(err.message || 'Failed to analyze portfolio. Please try again.')
    } finally {
      setLoading(false)
      setStreamProgress({ current: 0, total: 0, symbol: '', results: [] })
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          Investment Portfolio Builder
        </h1>
        <p className="text-lg text-gray-600">
          Create and manage your investment portfolio with ease
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="mr-2">📝</span>
            Portfolio Details
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Company Bucket Input */}
            <CompanyInput 
              companies={formData.companies}
              onChange={(companies) => handleInputChange('companies', companies)}
            />

            {/* Tenure Input */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Investment Tenure (Weeks)
              </label>
              <input
                type="number"
                min="1"
                max="520"
                value={formData.tenure}
                onChange={(e) => handleInputChange('tenure', e.target.value)}
                className="input-field"
                placeholder="Enter tenure in weeks (e.g., 52)"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                How long do you plan to invest?
              </p>
            </div>

            {/* Amount Input */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Investment Amount ($)
              </label>
              <input
                type="number"
                min="100"
                step="100"
                value={formData.amount}
                onChange={(e) => handleInputChange('amount', e.target.value)}
                className="input-field"
                placeholder="Enter amount (e.g., 10000)"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Total amount you want to invest
              </p>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => handleInputChange('startDate', e.target.value)}
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={formData.endDate}
                  onChange={(e) => handleInputChange('endDate', e.target.value)}
                  className="input-field"
                  required
                />
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex space-x-4">
              <button
                type="submit"
                className="btn-primary flex-1 relative"
                disabled={formData.companies.length === 0 || loading}
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing Portfolio...
                  </span>
                ) : (
                  'Calculate Portfolio'
                )}
              </button>
              {submitted && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="btn-secondary"
                  disabled={loading}
                >
                  Reset
                </button>
              )}
            </div>
            
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                <div className="flex items-start">
                  <span className="text-xl mr-2">⚠️</span>
                  <div>
                    <p className="font-semibold">Analysis Failed</p>
                    <p className="text-sm">{error}</p>
                  </div>
                </div>
              </div>
            )}
            
            {/* Loading Progress with Streaming Info */}
            {loading && (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">
                <div className="flex items-center mb-3">
                  <svg className="animate-spin h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <div>
                    <p className="font-semibold">AI Analysis in Progress</p>
                    <p className="text-sm">
                      {streamProgress.symbol ? (
                        <>Currently analyzing: <span className="font-bold">{streamProgress.symbol}</span> ({streamProgress.current}/{streamProgress.total})</>
                      ) : (
                        <>Starting analysis for {formData.companies.length} {formData.companies.length === 1 ? 'company' : 'companies'}...</>
                      )}
                    </p>
                    <p className="text-xs mt-1 italic">
                      ⏳ Please wait • {streamProgress.results.length} completed
                    </p>
                  </div>
                </div>
                
                {/* Progress Bar */}
                {streamProgress.total > 0 && (
                  <div className="w-full bg-blue-200 rounded-full h-2.5 mb-2">
                    <div 
                      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
                      style={{ width: `${(streamProgress.current / streamProgress.total) * 100}%` }}
                    ></div>
                  </div>
                )}
                
                {/* Completed Companies */}
                {streamProgress.results.length > 0 && (
                  <div className="mt-3 text-xs">
                    <p className="font-semibold mb-1">✅ Completed:</p>
                    <div className="flex flex-wrap gap-1">
                      {streamProgress.results.map((result, idx) => (
                        <span 
                          key={idx} 
                          className={`px-2 py-0.5 rounded ${result.status === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}
                        >
                          {result.symbol}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </form>
        </div>

        {/* Summary Display */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="mr-2">💰</span>
            Investment Summary
          </h2>
          
          {submitted && analysisResults ? (
            <InvestmentSummary 
              formData={formData} 
              analysisResults={analysisResults}
            />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400">
              <div className="text-center">
                <div className="text-6xl mb-4">📊</div>
                <p className="text-lg">
                  {loading 
                    ? 'Analyzing your portfolio...' 
                    : 'Fill in the details to see your investment summary'
                  }
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="text-4xl mb-3">🎯</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Smart Analysis</h3>
          <p className="text-gray-600">Advanced algorithms to analyze your portfolio</p>
        </div>
        <div className="card text-center">
          <div className="text-4xl mb-3">📈</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Real-time Data</h3>
          <p className="text-gray-600">Access live market data and insights</p>
        </div>
        <div className="card text-center">
          <div className="text-4xl mb-3">🔒</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Secure & Private</h3>
          <p className="text-gray-600">Your data is protected and encrypted</p>
        </div>
      </div>
    </div>
  )
}

export default Home

