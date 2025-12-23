import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
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
  // IMPORTANT: Append search params to the URL string, otherwise they are lost
  return <Navigate to={`/login${location.search}`} state={{ from: location }} replace />;
};

// Handle Zerodha callback that accidentally hit the frontend
const ZerodhaCallbackHandler = () => {
  const location = useLocation();

  useEffect(() => {
    // Redirect to backend with all query parameters
    const backendUrl = `http://localhost:8000/api/v1/auth/kite/callback${location.search}`;
    window.location.href = backendUrl;
  }, [location]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">Redirecting to Backend...</h2>
        <p className="text-gray-400">Completing authentication...</p>
      </div>
    </div>
  );
};

// Debug Component for 404
const NotFound = () => {
  const location = useLocation();
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <h1 className="text-4xl font-bold text-red-600 mb-4">404 - Not Found</h1>
      <p className="text-lg text-gray-700 mb-2">No route matched this location:</p>
      <code className="bg-gray-200 p-2 rounded text-sm font-mono mb-4 block">
        {location.pathname}
      </code>
      <p className="text-gray-500 text-sm">Query: {location.search}</p>
    </div>
  );
};

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <PortfolioProvider>
          <Routes>
            {/* Login Route */}
            <Route path="/login" element={<KiteLogin />} />

            {/* Handle backend callback hitting frontend - usage wildcard to be safe */}
            <Route path="/api/v1/auth/zerodha/*" element={<ZerodhaCallbackHandler />} />

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

            {/* Catch all for debugging */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </PortfolioProvider>
      </AuthProvider>
    </Router>
  )
}

export default App

