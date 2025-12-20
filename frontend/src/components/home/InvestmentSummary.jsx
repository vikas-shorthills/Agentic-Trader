const InvestmentSummary = ({ formData, analysisResults }) => {
  const { companies, tenure, amount } = formData
  
  const amountPerCompany = companies.length > 0 
    ? (parseFloat(amount) / companies.length).toFixed(2)
    : 0

  return (
    <div className="space-y-6">
      {/* Analysis Status */}
      {analysisResults && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-bold text-green-800">✅ AI Analysis Complete</h3>
            <span className="text-xs text-green-600 font-mono">
              {analysisResults.request_id}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-green-700">Successful: </span>
              <span className="font-bold text-green-900">
                {analysisResults.successful}/{analysisResults.total_companies}
              </span>
            </div>
            <div>
              <span className="text-green-700">Failed: </span>
              <span className="font-bold text-red-600">
                {analysisResults.failed}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-primary-50 to-primary-100 p-4 rounded-lg">
          <p className="text-sm text-primary-600 font-semibold">Total Investment</p>
          <p className="text-2xl font-bold text-primary-900">
            ${parseFloat(amount).toLocaleString()}
          </p>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
          <p className="text-sm text-green-600 font-semibold">Companies</p>
          <p className="text-2xl font-bold text-green-900">
            {companies.length}
          </p>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
          <p className="text-sm text-purple-600 font-semibold">Tenure</p>
          <p className="text-2xl font-bold text-purple-900">
            {tenure} Weeks
          </p>
        </div>
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
          <p className="text-sm text-orange-600 font-semibold">Per Company</p>
          <p className="text-2xl font-bold text-orange-900">
            ${parseFloat(amountPerCompany).toLocaleString()}
          </p>
        </div>
      </div>

      {/* AI Analysis Results */}
      {analysisResults && analysisResults.results && (
        <div>
          <h3 className="text-lg font-bold text-gray-800 mb-3">📊 AI Analysis Results</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {analysisResults.results.map((result, index) => (
              <div 
                key={index} 
                className={`p-4 rounded-lg border ${
                  result.status === 'success' 
                    ? 'bg-white border-green-200' 
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-bold text-lg text-gray-900">{result.symbol}</h4>
                    <span className={`text-xs font-semibold px-2 py-1 rounded ${
                      result.status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {result.status.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-primary-600 font-bold text-lg">
                    ${parseFloat(amountPerCompany).toLocaleString()}
                  </span>
                </div>
                
                {result.status === 'success' && result.analysis ? (
                  <div className="mt-3">
                    <details className="cursor-pointer">
                      <summary className="text-sm font-semibold text-blue-600 hover:text-blue-800">
                        📋 View Full Analysis
                      </summary>
                      <div className="mt-2 p-3 bg-gray-50 rounded text-xs font-mono whitespace-pre-wrap max-h-64 overflow-y-auto">
                        {result.analysis.raw_output}
                      </div>
                    </details>
                  </div>
                ) : result.error ? (
                  <div className="mt-2 text-sm text-red-600">
                    ⚠️ {result.error}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Company List (shown when no analysis yet) */}
      {!analysisResults && (
        <div>
          <h3 className="text-lg font-bold text-gray-800 mb-3">Selected Companies</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {companies.map((company, index) => (
              <div 
                key={index} 
                className="flex justify-between items-center bg-gray-50 p-3 rounded-lg border border-gray-200"
              >
                <span className="font-medium text-gray-800">{company}</span>
                <span className="text-primary-600 font-bold">
                  ${parseFloat(amountPerCompany).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default InvestmentSummary

