import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);
    const [error, setError] = useState(null);

    const checkAuth = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/kite/status`);
            const data = await response.json();

            if (data.is_authenticated) {
                setIsAuthenticated(true);
                setUser({
                    id: data.user_id,
                    expiresAt: data.expires_at
                });
            } else {
                setIsAuthenticated(false);
                setUser(null);
            }
        } catch (err) {
            console.error('Auth check failed:', err);
            setIsAuthenticated(false);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();

        // Poll status every 30 seconds to detect expiry/auto-logout
        const interval = setInterval(() => {
            checkAuth();
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    const login = async (token) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/auth/kite/save-token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ access_token: token })
            });

            const data = await response.json();

            if (data.success) {
                await checkAuth(); // Allow checkAuth to update state
                return { success: true };
            } else {
                throw new Error(data.error || 'Login failed');
            }
        } catch (err) {
            setError(err.message);
            return { success: false, error: err.message };
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            await fetch(`${API_BASE_URL}/auth/kite/logout`, { method: 'POST' });
            setIsAuthenticated(false);
            setUser(null);
        } catch (err) {
            console.error('Logout failed:', err);
        }
    };

    const value = {
        isAuthenticated,
        loading,
        user,
        error,
        login,
        logout,
        checkAuth
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
