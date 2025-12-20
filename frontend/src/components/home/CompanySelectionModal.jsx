import { useState, useEffect } from 'react'
import { fetchAllCompanies, fetchAllNSECompanies, searchCompanies } from '../../services/api'

const CompanySelectionModal = ({ isOpen, onClose, onAdd, existingCompanies }) => {
  const [activeTab, setActiveTab] = useState('nifty50')
  const [selectedCompanies, setSelectedCompanies] = useState({
    nifty50: [],
    nifty100: [],
    top200: [],
    custom: []
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [companyLists, setCompanyLists] = useState({
    nifty50: [],
    nifty100: [],
    top200: [],
    custom: []
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch company data from external APIs when modal opens
  useEffect(() => {
    if (isOpen && companyLists.nifty50.length === 0) {
      loadCompanyData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen])

  const loadCompanyData = async () => {
    setLoading(true)
    setError(null)
    try {
      // Fetch index lists and all NSE companies in parallel
      const [indexData, allNSE] = await Promise.all([
        fetchAllCompanies(),
        fetchAllNSECompanies()
      ])
      
      // Extract company symbols from all NSE data
      const allCompanySymbols = allNSE.map(company => 
        company.tradingsymbol || company.symbol || company
      )
      
      setCompanyLists({
        nifty50: indexData.nifty50 || [],
        nifty100: indexData.nifty100 || [],
        top200: indexData.top200 || [],
        custom: allCompanySymbols || []
      })
    } catch (err) {
      setError('Failed to load company lists from API.')
      console.error('Error loading companies:', err)
    } finally {
      setLoading(false)
    }
  }

  const getCompanyList = () => {
    // Use fetched data if available, otherwise empty array while loading
    if (loading) return []
    
    switch(activeTab) {
      case 'nifty50': return companyLists.nifty50
      case 'nifty100': return companyLists.nifty100
      case 'top200': return companyLists.top200
      case 'custom': return companyLists.custom
      default: return []
    }
  }

  const filteredCompanies = getCompanyList().filter(company => 
    company.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getCurrentTabSelections = () => {
    return selectedCompanies[activeTab] || []
  }

  const handleToggleCompany = (company) => {
    const currentSelections = getCurrentTabSelections()
    if (currentSelections.includes(company)) {
      setSelectedCompanies({
        ...selectedCompanies,
        [activeTab]: currentSelections.filter(c => c !== company)
      })
    } else {
      setSelectedCompanies({
        ...selectedCompanies,
        [activeTab]: [...currentSelections, company]
      })
    }
  }

  const handleSelectAll = () => {
    const currentList = getCompanyList()
    setSelectedCompanies({
      ...selectedCompanies,
      [activeTab]: currentList
    })
  }

  const handleDeselectAll = () => {
    setSelectedCompanies({
      ...selectedCompanies,
      [activeTab]: []
    })
  }

  const handleAddCompanies = () => {
    // Combine all selections from all tabs
    const allSelections = [
      ...selectedCompanies.nifty50,
      ...selectedCompanies.nifty100,
      ...selectedCompanies.top200,
      ...selectedCompanies.custom
    ]
    // Remove duplicates and filter out existing companies
    const uniqueSelections = [...new Set(allSelections)]
    const newCompanies = uniqueSelections.filter(c => !existingCompanies.includes(c))
    
    if (newCompanies.length > 0) {
      onAdd(newCompanies)
      setSelectedCompanies({
        nifty50: [],
        nifty100: [],
        top200: [],
        custom: []
      })
      setSearchTerm('')
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Select Companies</h2>
            <p className="text-sm text-gray-600 mt-1">Choose from curated lists or search for specific companies</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-3xl leading-none"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 px-6">
          <button
            onClick={() => setActiveTab('nifty50')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'nifty50'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Nifty 50
          </button>
          <button
            onClick={() => setActiveTab('nifty100')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'nifty100'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Nifty 100
          </button>
          <button
            onClick={() => setActiveTab('top200')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'top200'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Top 200
          </button>
          <button
            onClick={() => setActiveTab('custom')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'custom'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📋 All Companies {companyLists.custom.length > 0 && `(${companyLists.custom.length})`}
          </button>
        </div>

        {/* Search and Actions */}
        <div className="p-6 border-b border-gray-200">
          {/* Info banner for All Companies tab */}
          {activeTab === 'custom' && !loading && companyLists.custom.length > 0 && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200 text-blue-700 text-sm">
              <span className="font-semibold">📋 All NSE Companies:</span> Showing all {companyLists.custom.length} equity companies. Use search below to filter.
            </div>
          )}

          {/* Loading indicator */}
          {loading && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-sm flex items-center">
              <svg className="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Loading company data from API...</span>
            </div>
          )}
          
          {/* Error indicator */}
          {error && !loading && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={loadCompanyData}
                className="px-3 py-1 bg-yellow-100 hover:bg-yellow-200 rounded text-xs font-medium"
              >
                Retry
              </button>
            </div>
          )}
          
          <div className="flex space-x-4">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search companies..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              onClick={handleSelectAll}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              Select All
            </button>
            <button
              onClick={handleDeselectAll}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              Deselect All
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {activeTab === 'custom' ? (
              <>
                Showing: <span className="font-semibold text-primary-600">{filteredCompanies.length}</span> of <span className="font-semibold">{companyLists.custom.length}</span> companies • 
                Selected: <span className="font-semibold text-primary-600">{getCurrentTabSelections().length}</span>
              </>
            ) : (
              <>
                Selected: <span className="font-semibold text-primary-600">{getCurrentTabSelections().length}</span> companies
              </>
            )}
          </p>
        </div>

        {/* Company List */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <svg className="animate-spin h-12 w-12 mx-auto mb-4 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-gray-600">Fetching company data...</p>
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {filteredCompanies.map((company, index) => {
                  const isSelected = getCurrentTabSelections().includes(company)
                  const isExisting = existingCompanies.includes(company)
                  
                  return (
                    <label
                      key={index}
                      className={`flex items-center space-x-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        isExisting
                          ? 'border-gray-200 bg-gray-50 cursor-not-allowed opacity-50'
                          : isSelected
                          ? 'border-primary-600 bg-primary-50'
                          : 'border-gray-200 hover:border-primary-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleToggleCompany(company)}
                        disabled={isExisting}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500 cursor-pointer"
                      />
                      <span className={`text-sm font-medium ${isExisting ? 'text-gray-400' : 'text-gray-900'}`}>
                        {company}
                        {isExisting && <span className="text-xs ml-1">(Added)</span>}
                      </span>
                    </label>
                  )
                })}
              </div>
              {filteredCompanies.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-400 text-lg">No companies found</p>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 flex space-x-4">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleAddCompanies}
            disabled={selectedCompanies.nifty50.length + selectedCompanies.nifty100.length + selectedCompanies.top200.length + selectedCompanies.custom.length === 0}
            className="flex-1 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all"
          >
            Add {(selectedCompanies.nifty50.length + selectedCompanies.nifty100.length + selectedCompanies.top200.length + selectedCompanies.custom.length > 0) && 
              `(${[...new Set([...selectedCompanies.nifty50, ...selectedCompanies.nifty100, ...selectedCompanies.top200, ...selectedCompanies.custom])].length})`} Companies
          </button>
        </div>
      </div>
    </div>
  )
}

export default CompanySelectionModal

