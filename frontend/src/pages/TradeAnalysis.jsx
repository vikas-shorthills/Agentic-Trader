import { useState } from 'react'

const TradeAnalysis = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1M')

  const trades = [
    {
      id: 1,
      date: '2024-12-15',
      symbol: 'AAPL',
      type: 'BUY',
      quantity: 50,
      price: 175.20,
      total: 8760.00,
      currentPrice: 178.52,
      profit: 166.00,
      profitPercent: 1.89
    },
    {
      id: 2,
      date: '2024-12-10',
      symbol: 'TSLA',
      type: 'BUY',
      quantity: 25,
      price: 238.50,
      total: 5962.50,
      currentPrice: 242.84,
      profit: 108.50,
      profitPercent: 1.82
    },
    {
      id: 3,
      date: '2024-12-08',
      symbol: 'MSFT',
      type: 'BUY',
      quantity: 30,
      price: 378.30,
      total: 11349.00,
      currentPrice: 374.82,
      profit: -104.40,
      profitPercent: -0.92
    },
    {
      id: 4,
      date: '2024-12-05',
      symbol: 'AMZN',
      type: 'SELL',
      quantity: 40,
      price: 148.20,
      total: 5928.00,
      currentPrice: 151.94,
      profit: -149.60,
      profitPercent: -2.52
    }
  ]

  const timeframes = ['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL']

  const stats = {
    totalTrades: 24,
    winRate: 62.5,
    totalProfit: 3847.50,
    avgReturn: 2.34,
    bestTrade: 892.50,
    worstTrade: -245.30
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3 flex items-center">
          <span className="mr-3">📈</span>
          Trade Analysis
        </h1>
        <p className="text-lg text-gray-600">
          Track and analyze your trading performance
        </p>
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <div className="card bg-gradient-to-br from-primary-50 to-primary-100">
          <p className="text-sm text-primary-600 font-semibold mb-1">Total Trades</p>
          <p className="text-3xl font-bold text-primary-900">{stats.totalTrades}</p>
        </div>
        <div className="card bg-gradient-to-br from-green-50 to-green-100">
          <p className="text-sm text-green-600 font-semibold mb-1">Win Rate</p>
          <p className="text-3xl font-bold text-green-900">{stats.winRate}%</p>
        </div>
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
          <p className="text-sm text-blue-600 font-semibold mb-1">Total P&L</p>
          <p className="text-3xl font-bold text-blue-900">${stats.totalProfit.toLocaleString()}</p>
        </div>
        <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
          <p className="text-sm text-purple-600 font-semibold mb-1">Avg Return</p>
          <p className="text-3xl font-bold text-purple-900">{stats.avgReturn}%</p>
        </div>
        <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
          <p className="text-sm text-yellow-600 font-semibold mb-1">Best Trade</p>
          <p className="text-3xl font-bold text-yellow-900">${stats.bestTrade}</p>
        </div>
        <div className="card bg-gradient-to-br from-red-50 to-red-100">
          <p className="text-sm text-red-600 font-semibold mb-1">Worst Trade</p>
          <p className="text-3xl font-bold text-red-900">${stats.worstTrade}</p>
        </div>
      </div>

      {/* Timeframe Selection */}
      <div className="card mb-8">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Timeframe</h2>
        <div className="flex flex-wrap gap-2">
          {timeframes.map((timeframe) => (
            <button
              key={timeframe}
              onClick={() => setSelectedTimeframe(timeframe)}
              className={`px-6 py-2 rounded-lg font-semibold transition-all ${
                selectedTimeframe === timeframe
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {timeframe}
            </button>
          ))}
        </div>
      </div>

      {/* Recent Trades */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Recent Trades</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Symbol</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Type</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Quantity</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Entry Price</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Current Price</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">P&L</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Return %</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr key={trade.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-4 text-gray-700">
                    {new Date(trade.date).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </td>
                  <td className="py-4 px-4">
                    <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded font-mono font-semibold">
                      {trade.symbol}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className={`px-3 py-1 rounded font-semibold text-sm ${
                      trade.type === 'BUY' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {trade.type}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-right font-medium text-gray-700">{trade.quantity}</td>
                  <td className="py-4 px-4 text-right font-medium text-gray-700">
                    ${trade.price.toFixed(2)}
                  </td>
                  <td className="py-4 px-4 text-right font-medium text-gray-900">
                    ${trade.currentPrice.toFixed(2)}
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className={`font-bold ${trade.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {trade.profit >= 0 ? '+' : ''}${trade.profit.toFixed(2)}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className={`font-bold ${trade.profitPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {trade.profitPercent >= 0 ? '+' : ''}{trade.profitPercent.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Trading Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div className="card">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">💡</span>
            Key Insights
          </h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="text-2xl">✅</div>
              <div>
                <p className="font-semibold text-gray-800">Strong Performance</p>
                <p className="text-sm text-gray-600">Your win rate of 62.5% is above market average</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="text-2xl">📊</div>
              <div>
                <p className="font-semibold text-gray-800">Diversification</p>
                <p className="text-sm text-gray-600">Trading across 8 different sectors</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="text-2xl">⏱️</div>
              <div>
                <p className="font-semibold text-gray-800">Average Hold Time</p>
                <p className="text-sm text-gray-600">12.3 days per position</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">🎯</span>
            Recommendations
          </h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="text-2xl">🔔</div>
              <div>
                <p className="font-semibold text-gray-800">Risk Management</p>
                <p className="text-sm text-gray-600">Consider setting stop losses at -5%</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="text-2xl">📈</div>
              <div>
                <p className="font-semibold text-gray-800">Take Profits</p>
                <p className="text-sm text-gray-600">Lock in gains when positions reach +10%</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="text-2xl">💰</div>
              <div>
                <p className="font-semibold text-gray-800">Position Sizing</p>
                <p className="text-sm text-gray-600">Maintain 3-5% portfolio allocation per trade</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TradeAnalysis

