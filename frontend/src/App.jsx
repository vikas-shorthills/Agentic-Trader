import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Home from './pages/Home'
import Arena from './pages/Arena'
import ValueAnalysis from './pages/ValueAnalysis'
import TradeAnalysis from './pages/TradeAnalysis'
import KiteLogin from './pages/KiteLogin'
import { PortfolioProvider } from './contexts/PortfolioContext'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

// Helper to preserve query params on redirect
const RootRedirect = () => {
  const location = useLocation();
  return <Navigate to="/login" state={{ from: location }} search={location.search} replace />;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <PortfolioProvider>
          <Routes>
            {/* Login Route */}
            <Route path="/login" element={<KiteLogin />} />

            {/* Root Redirects to Login (preserving params for callbacks) */}
            <Route path="/" element={<RootRedirect />} />

            {/* Main App Routes with Layout */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout><Home /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/arena" element={
              <ProtectedRoute>
                <Layout><Arena /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/value-analysis" element={
              <ProtectedRoute>
                <Layout><ValueAnalysis /></Layout>
              </ProtectedRoute>
            } />
            <Route path="/trade-analysis" element={
              <ProtectedRoute>
                <Layout><TradeAnalysis /></Layout>
              </ProtectedRoute>
            } />
          </Routes>
        </PortfolioProvider>
      </AuthProvider>
    </Router>
  )
}

export default App

