import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Arena from './pages/Arena'
import ValueAnalysis from './pages/ValueAnalysis'
import TradeAnalysis from './pages/TradeAnalysis'
import KiteLogin from './pages/KiteLogin'
import { PortfolioProvider } from './contexts/PortfolioContext'

function App() {
  return (
    <Router>
      <PortfolioProvider>
        <Routes>
          {/* Kite Login - Default Landing Page */}
          <Route path="/" element={<KiteLogin />} />

          {/* Main App Routes with Layout */}
          <Route path="/dashboard" element={<Layout><Home /></Layout>} />
          <Route path="/arena" element={<Layout><Arena /></Layout>} />
          <Route path="/value-analysis" element={<Layout><ValueAnalysis /></Layout>} />
          <Route path="/trade-analysis" element={<Layout><TradeAnalysis /></Layout>} />
        </Routes>
      </PortfolioProvider>
    </Router>
  )
}

export default App

