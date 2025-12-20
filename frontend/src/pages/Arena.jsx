import { useState } from 'react'

const Arena = () => {
  const [selectedStock, setSelectedStock] = useState(null)

  const stocks = [
    { 
      id: 1, 
      name: 'Apple Inc.', 
      symbol: 'AAPL', 
      price: 178.52, 
      change: 2.34, 
      changePercent: 1.33,
      volume: '52.4M',
      marketCap: '2.81T'
    },
    { 
      id: 2, 
      name: 'Microsoft Corp.', 
      symbol: 'MSFT', 
      price: 374.82, 
      change: -1.24, 
      changePercent: -0.33,
      volume: '23.1M',
      marketCap: '2.78T'
    },
    { 
      id: 3, 
      name: 'Tesla Inc.', 
      symbol: 'TSLA', 
      price: 242.84, 
      change: 5.67, 
      changePercent: 2.39,
      volume: '98.3M',
      marketCap: '771.2B'
    },
    { 
      id: 4, 
      name: 'Amazon.com Inc.', 
      symbol: 'AMZN', 
      price: 151.94, 
      change: 0.87, 
      changePercent: 0.58,
      volume: '47.2M',
      marketCap: '1.57T'
    },
    { 
      id: 5, 
      name: 'Alphabet Inc.', 
      symbol: 'GOOGL', 
      price: 139.67, 
      change: -0.45, 
      changePercent: -0.32,
      volume: '21.8M',
      marketCap: '1.76T'
    },
    { 
      id: 6, 
      name: 'NVIDIA Corp.', 
      symbol: 'NVDA', 
      price: 495.23, 
      change: 8.92, 
      changePercent: 1.84,
      volume: '41.5M',
      marketCap: '1.22T'
    },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3 flex items-center">
          <span className="mr-3">🎯</span>
          Trading Arena
        </h1>
        <p className="text-lg text-gray-600">
          Monitor real-time market data and compare top stocks
        </p>
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
          <p className="text-sm text-blue-600 font-semibold mb-1">Market Status</p>
          <p className="text-2xl font-bold text-blue-900">Open</p>
          <p className="text-xs text-blue-600 mt-1">NYSE</p>
        </div>
        <div className="card bg-gradient-to-br from-green-50 to-green-100">
          <p className="text-sm text-green-600 font-semibold mb-1">Gainers</p>
          <p className="text-2xl font-bold text-green-900">127</p>
          <p className="text-xs text-green-600 mt-1">Today</p>
        </div>
        <div className="card bg-gradient-to-br from-red-50 to-red-100">
          <p className="text-sm text-red-600 font-semibold mb-1">Losers</p>
          <p className="text-2xl font-bold text-red-900">89</p>
          <p className="text-xs text-red-600 mt-1">Today</p>
        </div>
        <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
          <p className="text-sm text-purple-600 font-semibold mb-1">Volume</p>
          <p className="text-2xl font-bold text-purple-900">2.4B</p>
          <p className="text-xs text-purple-600 mt-1">Total</p>
        </div>
      </div>

      {/* Stock List */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Top Stocks</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Company</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Symbol</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Price</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Change</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Volume</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Market Cap</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Action</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((stock) => (
                <tr 
                  key={stock.id} 
                  className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-4 px-4 font-medium text-gray-900">{stock.name}</td>
                  <td className="py-4 px-4">
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded font-mono text-sm">
                      {stock.symbol}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-right font-bold text-gray-900">
                    ${stock.price.toFixed(2)}
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className={`font-semibold ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent >= 0 ? '+' : ''}{stock.changePercent}%)
                    </span>
                  </td>
                  <td className="py-4 px-4 text-right text-gray-600">{stock.volume}</td>
                  <td className="py-4 px-4 text-right text-gray-600">${stock.marketCap}</td>
                  <td className="py-4 px-4 text-center">
                    <button
                      onClick={() => setSelectedStock(stock)}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all text-sm font-medium"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stock Detail Modal/Panel */}
      {selectedStock && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-8">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-3xl font-bold text-gray-900">{selectedStock.name}</h3>
                <p className="text-lg text-gray-600">{selectedStock.symbol}</p>
              </div>
              <button
                onClick={() => setSelectedStock(null)}
                className="text-gray-400 hover:text-gray-600 text-3xl"
              >
                ×
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Current Price</p>
                <p className="text-3xl font-bold text-gray-900">${selectedStock.price.toFixed(2)}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Change</p>
                <p className={`text-3xl font-bold ${selectedStock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {selectedStock.change >= 0 ? '+' : ''}{selectedStock.change.toFixed(2)}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Volume</p>
                <p className="text-xl font-bold text-gray-900">{selectedStock.volume}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Market Cap</p>
                <p className="text-xl font-bold text-gray-900">${selectedStock.marketCap}</p>
              </div>
            </div>

            <div className="flex space-x-4">
              <button className="btn-primary flex-1">Buy</button>
              <button className="btn-secondary flex-1">Add to Watchlist</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Arena

