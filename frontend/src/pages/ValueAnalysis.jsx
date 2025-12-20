import { useState } from 'react'

const ValueAnalysis = () => {
  const [selectedMetric, setSelectedMetric] = useState('pe')

  const companies = [
    {
      id: 1,
      name: 'Apple Inc.',
      symbol: 'AAPL',
      peRatio: 29.5,
      pbRatio: 42.3,
      debtToEquity: 1.89,
      roe: 147.3,
      divYield: 0.52,
      rating: 'Strong Buy'
    },
    {
      id: 2,
      name: 'Microsoft Corp.',
      symbol: 'MSFT',
      peRatio: 34.8,
      pbRatio: 11.9,
      debtToEquity: 0.42,
      roe: 42.1,
      divYield: 0.81,
      rating: 'Buy'
    },
    {
      id: 3,
      name: 'Tesla Inc.',
      symbol: 'TSLA',
      peRatio: 72.4,
      pbRatio: 14.2,
      debtToEquity: 0.15,
      roe: 28.5,
      divYield: 0.0,
      rating: 'Hold'
    },
    {
      id: 4,
      name: 'Amazon.com Inc.',
      symbol: 'AMZN',
      peRatio: 52.1,
      pbRatio: 8.7,
      debtToEquity: 0.61,
      roe: 17.8,
      divYield: 0.0,
      rating: 'Buy'
    }
  ]

  const metrics = [
    { id: 'pe', name: 'P/E Ratio', description: 'Price to Earnings', icon: '📊' },
    { id: 'pb', name: 'P/B Ratio', description: 'Price to Book', icon: '📈' },
    { id: 'de', name: 'Debt/Equity', description: 'Debt to Equity Ratio', icon: '💰' },
    { id: 'roe', name: 'ROE', description: 'Return on Equity', icon: '🎯' },
    { id: 'div', name: 'Div Yield', description: 'Dividend Yield', icon: '💵' }
  ]

  const getRatingColor = (rating) => {
    switch(rating) {
      case 'Strong Buy': return 'bg-green-100 text-green-800'
      case 'Buy': return 'bg-blue-100 text-blue-800'
      case 'Hold': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3 flex items-center">
          <span className="mr-3">📊</span>
          Value Analysis
        </h1>
        <p className="text-lg text-gray-600">
          Comprehensive fundamental analysis and valuation metrics
        </p>
      </div>

      {/* Metrics Selection */}
      <div className="card mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Select Analysis Metric</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {metrics.map((metric) => (
            <button
              key={metric.id}
              onClick={() => setSelectedMetric(metric.id)}
              className={`p-4 rounded-lg border-2 transition-all text-center ${
                selectedMetric === metric.id
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300'
              }`}
            >
              <div className="text-3xl mb-2">{metric.icon}</div>
              <p className="font-bold text-gray-900">{metric.name}</p>
              <p className="text-xs text-gray-600">{metric.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Company Comparison Table */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Company Comparison</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Company</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">P/E Ratio</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">P/B Ratio</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">D/E Ratio</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">ROE (%)</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Div Yield (%)</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Rating</th>
              </tr>
            </thead>
            <tbody>
              {companies.map((company) => (
                <tr key={company.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-4">
                    <div>
                      <p className="font-bold text-gray-900">{company.name}</p>
                      <p className="text-sm text-gray-600">{company.symbol}</p>
                    </div>
                  </td>
                  <td className={`py-4 px-4 text-center font-semibold ${selectedMetric === 'pe' ? 'bg-primary-50 text-primary-900' : 'text-gray-700'}`}>
                    {company.peRatio.toFixed(1)}
                  </td>
                  <td className={`py-4 px-4 text-center font-semibold ${selectedMetric === 'pb' ? 'bg-primary-50 text-primary-900' : 'text-gray-700'}`}>
                    {company.pbRatio.toFixed(1)}
                  </td>
                  <td className={`py-4 px-4 text-center font-semibold ${selectedMetric === 'de' ? 'bg-primary-50 text-primary-900' : 'text-gray-700'}`}>
                    {company.debtToEquity.toFixed(2)}
                  </td>
                  <td className={`py-4 px-4 text-center font-semibold ${selectedMetric === 'roe' ? 'bg-primary-50 text-primary-900' : 'text-gray-700'}`}>
                    {company.roe.toFixed(1)}%
                  </td>
                  <td className={`py-4 px-4 text-center font-semibold ${selectedMetric === 'div' ? 'bg-primary-50 text-primary-900' : 'text-gray-700'}`}>
                    {company.divYield.toFixed(2)}%
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getRatingColor(company.rating)}`}>
                      {company.rating}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Analysis Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="card bg-gradient-to-br from-green-50 to-green-100">
          <div className="text-3xl mb-3">✅</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Best Value</h3>
          <p className="text-gray-700 font-semibold">Microsoft Corp.</p>
          <p className="text-sm text-gray-600 mt-1">Balanced metrics and strong fundamentals</p>
        </div>
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
          <div className="text-3xl mb-3">📈</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Highest ROE</h3>
          <p className="text-gray-700 font-semibold">Apple Inc.</p>
          <p className="text-sm text-gray-600 mt-1">147.3% return on equity</p>
        </div>
        <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
          <div className="text-3xl mb-3">💎</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Best Dividend</h3>
          <p className="text-gray-700 font-semibold">Microsoft Corp.</p>
          <p className="text-sm text-gray-600 mt-1">0.81% dividend yield</p>
        </div>
      </div>
    </div>
  )
}

export default ValueAnalysis

