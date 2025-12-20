import { createContext, useContext, useState } from 'react'

const PortfolioContext = createContext()

export const usePortfolio = () => {
  const context = useContext(PortfolioContext)
  if (!context) {
    throw new Error('usePortfolio must be used within PortfolioProvider')
  }
  return context
}

export const PortfolioProvider = ({ children }) => {
  const [formData, setFormData] = useState({
    companies: [],
    tenure: '',
    amount: '',
    startDate: '',
    endDate: ''
  })
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [error, setError] = useState(null)
  const [streamProgress, setStreamProgress] = useState({ 
    current: 0, 
    total: 0, 
    symbol: '', 
    results: [] 
  })

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleReset = () => {
    setFormData({
      companies: [],
      tenure: '',
      amount: '',
      startDate: '',
      endDate: ''
    })
    setSubmitted(false)
    setAnalysisResults(null)
    setError(null)
    setStreamProgress({ current: 0, total: 0, symbol: '', results: [] })
  }

  const value = {
    formData,
    setFormData,
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
  }

  return (
    <PortfolioContext.Provider value={value}>
      {children}
    </PortfolioContext.Provider>
  )
}

