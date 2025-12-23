import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { CheckCircle, XCircle, Loader2, BarChart2, Zap, Shield, ArrowRight } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

// Configuration
const KITE_API_KEY = '2j2xf518ahokaidb'
const API_BASE_URL = 'http://localhost:8000/api/v1'

export default function KiteLogin() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const { isAuthenticated, loading, user, login, logout, checkAuth } = useAuth()

    // Local state for UI feedback during login process
    const [loginStatus, setLoginStatus] = useState(null)
    const [isProcessing, setIsProcessing] = useState(false)

    useEffect(() => {
        // Handle Kite Callback
        const requestToken = searchParams.get('request_token')
        const status = searchParams.get('status')
        const kiteAuth = searchParams.get('kite_auth')
        const error = searchParams.get('error')

        if (requestToken && status === 'success') {
            // Direct callback to frontend (legacy/manual)
            handleLogin(requestToken)
        } else if (kiteAuth === 'success') {
            // Redirect from backend after successful auth
            checkAuth().then(() => {
                setLoginStatus({ success: true })
                setTimeout(() => navigate('/dashboard'), 1500)
            })
        } else if (status === 'error' || kiteAuth === 'failed') {
            setLoginStatus({ success: false, error: error || 'Authorization denied' })
        }
    }, [searchParams])

    const handleLogin = async (token) => {
        setIsProcessing(true)
        const result = await login(token)

        if (result.success) {
            setLoginStatus({ success: true })
            // Optional: Auto redirect after success?
            // setTimeout(() => navigate('/dashboard'), 1500)
        } else {
            setLoginStatus({ success: false, error: result.error })
        }
        setIsProcessing(false)
    }

    const handleConnectToKite = () => {
        // Redirect to backend login endpoint which handles the Zerodha redirection
        // This ensures the backend and frontend use the exact same API_KEY
        window.location.href = `${API_BASE_URL}/auth/kite/login`
    }

    const handleLogout = async () => {
        await logout()
        setLoginStatus(null)
    }

    // Show global loading state only on initial load
    // We handle "processing" state locally for better UX control
    if (loading && !loginStatus) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-[#0f111a]">
                <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-[#0f111a] flex items-center justify-center p-4">
            <div className="bg-[#1a1d2d] rounded-2xl shadow-2xl p-8 max-w-[420px] w-full border border-gray-800/50">
                {/* Logo Section */}
                <div className="flex flex-col items-center mb-8">
                    <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-4">
                        <BarChart2 className="w-6 h-6 text-blue-500" />
                    </div>
                    <h1 className="text-2xl font-bold text-white mb-2">
                        Athena<span className="text-blue-500">Trader</span>
                    </h1>
                    <p className="text-gray-400 text-center text-sm px-4">
                        Elevate your trading with precision and intelligence.
                    </p>
                </div>

                {/* Main Content */}
                <div className="space-y-8">
                    {/* Features */}
                    <div className="space-y-6">
                        <div className="flex items-start gap-4">
                            <Zap className="w-5 h-5 text-blue-400 mt-1 shrink-0" />
                            <div>
                                <h3 className="text-gray-200 text-sm font-semibold">Direct Zerodha Integration</h3>
                                <p className="text-gray-500 text-xs mt-0.5">Seamlessly connect your Kite account.</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-4">
                            <Shield className="w-5 h-5 text-green-400 mt-1 shrink-0" />
                            <div>
                                <h3 className="text-gray-200 text-sm font-semibold">Secure Authentication</h3>
                                <p className="text-gray-500 text-xs mt-0.5">Your credentials never touch our servers.</p>
                            </div>
                        </div>
                    </div>

                    {/* Feedback States */}
                    <div>
                        {isProcessing && (
                            <div className="text-center py-4 bg-blue-500/5 rounded-lg mb-4">
                                <Loader2 className="w-6 h-6 text-blue-500 animate-spin mx-auto mb-2" />
                                <p className="text-blue-400 text-sm">Authenticating...</p>
                            </div>
                        )}

                        {loginStatus?.success && (
                            <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg flex items-center gap-3 mb-4">
                                <CheckCircle className="w-5 h-5 text-green-500" />
                                <span className="text-green-400 text-sm font-medium">Successfully Connected</span>
                            </div>
                        )}

                        {loginStatus?.success === false && (
                            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-3 mb-4">
                                <XCircle className="w-5 h-5 text-red-500" />
                                <span className="text-red-400 text-sm font-medium">{loginStatus.error || 'Connection Failed'}</span>
                            </div>
                        )}

                        {/* Session Status Display */}
                        {!isProcessing && isAuthenticated && user && (
                            <div className="mb-4 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-medium text-gray-400">Status</span>
                                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-green-500/10 text-green-500">
                                        Active
                                    </span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium text-gray-400">User ID</span>
                                    <span className="text-sm text-gray-200 font-mono">{user.id}</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Action Buttons */}
                    <div className="space-y-3">
                        {!isAuthenticated ? (
                            <button
                                onClick={handleConnectToKite}
                                disabled={isProcessing}
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 px-6 rounded-xl
                                transition-all duration-200 flex items-center justify-center gap-2 
                                disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-600/20"
                            >
                                <span className="text-sm">Connect with Zerodha</span>
                                <ArrowRight className="w-4 h-4" />
                            </button>
                        ) : (
                            <>
                                <button
                                    onClick={() => navigate('/dashboard')}
                                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 px-6 rounded-xl
                                    transition-all duration-200 shadow-lg shadow-blue-600/20 text-sm"
                                >
                                    Go to Dashboard
                                </button>
                                <button
                                    onClick={handleLogout}
                                    className="w-full bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold py-3.5 px-6 rounded-xl
                                    transition-all duration-200 text-sm border border-gray-700"
                                >
                                    Disconnect
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center px-4">
                    <p className="text-[10px] text-gray-600 leading-relaxed">
                        By connecting, you agree to our Terms of Service and Privacy Policy.
                    </p>
                </div>
            </div>
        </div>
    )
}
