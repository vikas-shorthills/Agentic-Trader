import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Arena from './pages/Arena'
import ValueAnalysis from './pages/ValueAnalysis'
import TradeAnalysis from './pages/TradeAnalysis'
import { PortfolioProvider } from './contexts/PortfolioContext'

function App() {
  return (
    <Router>
      <PortfolioProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/arena" element={<Arena />} />
            <Route path="/value-analysis" element={<ValueAnalysis />} />
            <Route path="/trade-analysis" element={<TradeAnalysis />} />
          </Routes>
        </Layout>
      </PortfolioProvider>
    </Router>
  )
}

export default App

