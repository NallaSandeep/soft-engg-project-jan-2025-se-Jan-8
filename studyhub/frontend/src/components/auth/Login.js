import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../common/Button';
import Input from '../common/Input';
import { Card } from '../common/Card';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const { login } = useAuth();

    useEffect(() => {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        console.log("Email: ", email);
        console.log("Password: ", password);
        console.log("Remember me: ", rememberMe);

        try {
            const result = await login({ email, password, rememberMe });
            if (!result.success) {
                console.log('Login failed:', result.error);
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
        <div className="flex items-center justify-center min-h-screen bg-zinc-50 dark:bg-zinc-900">
            <div className="w-full max-w-md">
                <Card className="overflow-hidden">
                    <div className="px-8 py-6 bg-white dark:bg-zinc-800">
                        <div className="text-center mb-6">
                            <h2 className="text-2xl font-bold text-zinc-900 dark:text-white">
                                StudyHub
                            </h2>
                        </div>

                        {error && (
                            <div className="mb-6 p-3 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-800">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        Email Address
                                    </label>
                                    <Input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        disabled={loading}
                                        required
                                        fullWidth
                                        placeholder="Enter your email"
                                        className="dark:bg-zinc-700 dark:border-zinc-600"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        Password
                                    </label>
                                    <Input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        disabled={loading}
                                        required
                                        fullWidth
                                        placeholder="••••••••"
                                        className="dark:bg-zinc-700 dark:border-zinc-600"
                                    />
                                </div>
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <input
                                        id="remember-me"
                                        name="remember-me"
                                        type="checkbox"
                                        checked={rememberMe}
                                        onChange={(e) => setRememberMe(e.target.checked)}
                                        className="h-4 w-4 text-blue-600 dark:text-gray-400 focus:ring-gray-500 dark:focus:ring-gray-400 rounded dark:bg-zinc-700"
                                    />
                                    <label htmlFor="remember-me" className="ml-2 block text-sm text-zinc-700 dark:text-zinc-300">
                                        Remember me
                                    </label>
                                </div>
                                {/* <div className="text-sm">
                                    <a 
                                        href="/forgot-password"
                                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                                    >
                                        Forgot password?
                                    </a>
                                </div> */}
                            </div>

                            <Button
                                type="submit"
                                variant="primary"
                                disabled={loading}
                                loading={loading}
                                fullWidth
                                className="bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600"
                            >
                                {loading ? 'Signing in...' : 'Sign in'}
                            </Button>

                            <div className="text-center text-sm text-zinc-600 dark:text-zinc-400">
                                Don't have an account?{' '}
                                <a 
                                    href="/register"
                                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                                >
                                    Create one now
                                </a>
                            </div>
                        </form>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default Login; 