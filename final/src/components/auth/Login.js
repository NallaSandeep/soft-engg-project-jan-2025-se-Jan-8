import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const mockUsers = {
    "admin@studyhub.com": { password: "admin123", role: "admin" },
    "student@studyhub.com": { password: "student123", role: "student" },
    "ta@studyhub.com": { password: "ta123", role: "ta" }
};

const redirectPaths = {
    admin: '/admin/dashboard',
    student: '/student/dashboard',
    ta: '/ta/dashboard'
};

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        setTimeout(() => {
            if (mockUsers[email] && mockUsers[email].password === password) {
                const role = mockUsers[email].role;
                sessionStorage.setItem("userEmail", email);
                sessionStorage.setItem("userRole", role);
                navigate(redirectPaths[role] || "/dashboard");
            } else {
                setError('Invalid email or password');
            }
            setLoading(false);
        }, 1000);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-zinc-100 to-white dark:from-zinc-900 dark:to-black p-6 font-mono">
            <div className="w-full max-w-md animate-fade-in">
                <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl rounded-2xl shadow-md overflow-hidden">
                <div className="text-center pt-8">
                    <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
                        StudyHub
                    </h1>
                </div>
                    <div className="p-7">
                        {error && (
                            <div className="mb-4 pt-3 bg-red-100 dark:bg-red-900 border-l-4 border-red-500 rounded-md flex items-center justify-center">
                                <p className="text-xs text-red-700 dark:text-red-300">
                                    {error}
                                </p>
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-1">
                                        Email Address
                                    </label>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        disabled={loading}
                                        className="w-full px-3 py-2.5 bg-zinc-100 dark:bg-zinc-800 
                                        border border-zinc-300 dark:border-zinc-600 text-sm
                                        text-zinc-900 dark:text-zinc-100 rounded-md 
                                        focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500
                                        focus:ring-1 focus:ring-zinc-400 dark:focus:ring-zinc-500
                                        disabled:opacity-50 disabled:cursor-not-allowed
                                        transition-all duration-200 font-medium"
                                        placeholder="Enter your email"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-1">
                                        Password
                                    </label>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        disabled={loading}
                                        className="w-full px-3 py-2.5 bg-zinc-100 dark:bg-zinc-800 
                                        border border-zinc-300 dark:border-zinc-600 text-sm
                                        text-zinc-900 dark:text-zinc-100 rounded-md 
                                        focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500
                                        focus:ring-1 focus:ring-zinc-400 dark:focus:ring-zinc-500
                                        disabled:opacity-50 disabled:cursor-not-allowed
                                            transition-all duration-200"
                                        placeholder="• • • • • • • •"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="flex items-center justify-between">
                                <label className="flex items-center">
                                    <input type="checkbox" className="w-4 h-4 rounded border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 focus:ring-zinc-900 dark:focus:ring-zinc-100 bg-white dark:bg-zinc-900"/>
                                    <span className="ml-2 text-sm text-zinc-600 dark:text-zinc-400 text-xs ">Remember me</span>
                                </label>
                                <a href="/forgot-password" className="text-xs text-zinc-900 dark:text-zinc-100 hover:text-zinc-700 dark:hover:text-zinc-300">
                                    Forgot password?
                                </a>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className={`w-full px-4 py-3 text-zinc-100 dark:text-zinc-900 font-medium bg-zinc-800 dark:bg-white rounded-md hover:bg-zinc-700 dark:hover:bg-zinc-100 focus:outline-none focus:ring-2 focus:ring-zinc-900 dark:focus:ring-zinc-100 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-zinc-900 transition-all duration-200 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {loading ? (
                                    <div className="flex items-center justify-center font-medium">
                                        <svg className="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                                        </svg>
                                        Signing in...
                                    </div>
                                ) : 'Sign in'}
                            </button>
                        </form>

                        <div className="mt-6 text-center border-t border-zinc-200 dark:border-zinc-800 pt-6">
                            <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                Don't have an account?{' '}
                                <a href="/register" className="font-medium text-zinc-900 dark:text-zinc-100 hover:text-zinc-700 dark:hover:text-zinc-300">
                                    Create one now
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;