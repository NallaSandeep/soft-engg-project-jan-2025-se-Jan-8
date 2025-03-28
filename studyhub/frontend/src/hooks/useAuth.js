import { useState, useEffect, useContext, createContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../services/apiService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');
            if (token) {
                const response = await authApi.getCurrentUser();
                if (response && response.user) {
                    setUser(response.user);
                } else {
                    localStorage.removeItem('token');
                    sessionStorage.removeItem('token');
                    setUser(null);
                }
            }
        } catch (err) {
            localStorage.removeItem('token');
            sessionStorage.removeItem('token');
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (credentials) => {
        try {
            const response = await authApi.login(credentials);
            if (response.success) {
                localStorage.setItem('token', response.data.access_token);
                setUser(response.data.user);
                
                // Redirect based on user role
                switch (response.data.user.role) {
                    case 'admin':
                        navigate('/admin/dashboard');
                        break;
                    case 'ta':
                        navigate('/ta/courses');
                        break;
                    case 'student':
                        navigate('/student/dashboard');
                        break;
                    default:
                        navigate('/');
                }
                
                return { success: true };
            } else {
                return { 
                    success: false, 
                    error: response.message || response.error || 'Login failed' 
                };
            }
        } catch (err) {
            console.error('Login failed:', err);
            return { 
                success: false, 
                error: err.message || 'Login failed' 
            };
        }
    };

    const register = async (userData) => {
        try {
            const response = await authApi.register(userData);
            if (response.success) {
                // localStorage.setItem('token', response.data.access_token);
                // setUser(response.data.user);
                // navigate('/login');
                return { success: true };
            } else {
                return { 
                    success: false, 
                    error: response.message || response.msg || response.error || 'Registration failed' 
                };
            }
        } catch (err) {
            console.error('Registration failed:', err);
            return { 
                success: false, 
                error: err.message || err.msg || 'Registration failed' 
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
        navigate('/login');
    };

    const updateProfile = async (userData) => {
        try {
            const response = await authApi.updateProfile(userData);
            if (response.success) {
                setUser(response.data.user);
                return { success: true };
            } else {
                return { 
                    success: false, 
                    error: response.message || response.error || 'Profile update failed' 
                };
            }
        } catch (err) {
            console.error('Profile update failed:', err);
            return { 
                success: false, 
                error: err.message || 'Profile update failed' 
            };
        }
    };

    const value = {
        user,
        loading,
        login,
        register,
        logout,
        updateProfile
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default useAuth; 