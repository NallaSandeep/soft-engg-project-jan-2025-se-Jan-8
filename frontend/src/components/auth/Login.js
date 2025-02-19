import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../common/Button';
import Input from '../common/Input';
import { Card } from '../common/Card';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const result = await login({ email, password });
            if (!result.success) {
                setError(result.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            setError(error.message || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };
    
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-100 to-white dark:from-gray-900 dark:to-gray-800 p-6">
                <div>
                    {/* Header Section */}
                    <div className="text-center mb-8">
                        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                            StudyHub
                        </h1>
                        <p className="text-gray-600 dark:text-gray-400">
                            Welcome back! Please sign in to continue.
                        </p>
                    </div>
    
                    {/* Login Card */}
                    <Card className="bg-white dark:bg-gray-800 rounded-md">
                        <div className="p-8">
                            {/* Error Message */}
                            {error && (
                                <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/10 border-l-4 border-red-500 rounded">
                                    <p className="text-sm text-red-600 dark:text-red-400 flex items-center">
                                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        {error}
                                    </p>
                                </div>
                            )}
    
                            {/* Login Form */}
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div className="space-y-4">
                                    <Input
                                        type="email"
                                        label="Email address"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        disabled={loading}
                                        required
                                        fullWidth
                                        placeholder="john@example.com"
                                        className="bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 rounded-sm focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
                                    />
    
                                    <Input
                                        type="password"
                                        label="Password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        disabled={loading}
                                        required
                                        fullWidth
                                        placeholder="••••••••"
                                        className="bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 rounded-sm focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
                                    />
                                </div>
    
                                {/* Remember Me & Forgot Password */}
                                <div className="flex items-center justify-between">
                                    <label className="flex items-center cursor-pointer group">
                                        <input 
                                            type="checkbox" 
                                            className="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-blue-500 focus:ring-blue-500"
                                        />
                                        <span className="ml-2 text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-300">
                                            Remember me
                                        </span>
                                    </label>
                                    <a href="/forgot-password" 
                                       className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
                                        Forgot password?
                                    </a>
                                </div>
    
                                {/* Submit Button */}
                                <Button
                                    type="submit"
                                    disabled={loading}
                                    loading={loading}
                                    fullWidth
                                    className="bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-sm font-medium transition-all duration-150 transform hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {loading ? (
                                        <div className="flex items-center justify-center">
                                            <svg className="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                            </svg>
                                            Signing in...
                                        </div>
                                    ) : 'Sign in'}
                                </Button>
                            </form>
    
                            {/* Sign Up Link */}
                            <div className="mt-6 text-center border-t border-gray-200 dark:border-gray-700 pt-6">
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Don't have an account?{' '}
                                    <a href="/register" 
                                       className="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
                                        Create one now
                                    </a>
                                </p>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        );
    };

export default Login;