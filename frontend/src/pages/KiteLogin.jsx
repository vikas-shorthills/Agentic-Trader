import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

// Configuration
const KITE_API_KEY = '2j2xf518ahokaidb'

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

        if (requestToken && status === 'success') {
            handleLogin(requestToken)
        } else if (status === 'error') {
            setLoginStatus({ success: false, error: 'Authorization denied from Kite' })
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
        // Redirect directly to Kite login with our frontend as the redirect URL
        // In production, this should ideally come from backend config
        const kiteLoginUrl = `https://kite.zerodha.com/connect/login?api_key=${KITE_API_KEY}&v=3`
        window.location.href = kiteLoginUrl
    }

    const handleLogout = async () => {
        await logout()
        setLoginStatus(null)
    }

    // Show global loading state only on initial load
    // We handle "processing" state locally for better UX control
    if (loading && !loginStatus) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader2 className="w-12 h-12 text-indigo-600 animate-spin" />
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
            <div className="max-w-md w-full">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
                        Kite Connect
                    </h1>
                    <p className="text-gray-600">
                        Connect your Zerodha Kite account to start trading
                    </p>
                </div>

                {/* Main Card */}
                <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
                    {/* Processing State */}
                    {isProcessing && (
                        <div className="text-center py-8">
                            <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
                            <p className="text-gray-600">Authenticating with Kite...</p>
                        </div>
                    )}

                    {/* Success Message */}
                    {loginStatus?.success && (
                        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
                            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                            <div>
                                <h3 className="font-semibold text-green-900">Successfully Connected!</h3>
                                <p className="text-sm text-green-700 mt-1">
                                    Your Kite account is now connected.
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Error Message */}
                    {loginStatus?.success === false && (
                        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                            <XCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                            <div>
                                <h3 className="font-semibold text-red-900">Connection Failed</h3>
                                <p className="text-sm text-red-700 mt-1">
                                    {loginStatus.error || 'An error occurred during authentication'}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Session Status Display */}
                    {!isProcessing && isAuthenticated && user && (
                        <div className="mb-6">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium text-gray-700">Status:</span>
                                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                                    Connected
                                </span>
                            </div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium text-gray-700">User ID:</span>
                                <span className="text-sm text-gray-900">{user.id}</span>
                            </div>
                            {user.expiresAt && (
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium text-gray-700">Expires:</span>
                                    <span className="text-sm text-gray-900">
                                        {new Date(user.expiresAt).toLocaleString()}
                                    </span>
                                </div>
                            )}
                        </div>
                    )}

                    {!isProcessing && !isAuthenticated && !loginStatus?.success && !loginStatus?.error && (
                        <div className="mb-6 text-center">
                            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800">
                                Not Connected
                            </span>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="space-y-3">
                        {!isAuthenticated ? (
                            <button
                                onClick={handleConnectToKite}
                                disabled={isProcessing}
                                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg
                         hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02]
                         shadow-lg hover:shadow-xl flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" />
                                </svg>
                                Connect to Kite
                            </button>
                        ) : (
                            <>
                                <button
                                    onClick={() => navigate('/dashboard')}
                                    className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg
                           hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02]
                           shadow-lg hover:shadow-xl"
                                >
                                    Go to Dashboard
                                </button>
                                <button
                                    onClick={handleLogout}
                                    className="w-full bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-lg
                           hover:bg-gray-200 transition-all duration-200"
                                >
                                    Disconnect
                                </button>
                            </>
                        )}
                    </div>

                    {/* Info Text */}
                    <div className="mt-6 pt-6 border-t border-gray-100">
                        <p className="text-xs text-gray-500 text-center">
                            By connecting, you authorize this application to access your Kite account.
                            Your credentials are never stored.
                        </p>
                    </div>
                </div>

                {/* Footer Info */}
                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-600">
                        Powered by <span className="font-semibold">Zerodha Kite</span>
                    </p>
                </div>
            </div>
        </div>
    )
}
