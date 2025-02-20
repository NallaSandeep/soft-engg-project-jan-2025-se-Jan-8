import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: ''
    });
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (error) setError(null);
    };

    const validateForm = () => {
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return false;
        }
        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            return false;
        }
        return true;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!validateForm()) return;
        setLoading(true);
        setTimeout(() => setLoading(false), 1000); // Simulating a request
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-zinc-100 to-white dark:from-zinc-900 dark:to-black p-6 font-mono">
            <div className="w-full max-w-md animate-fade-in">
                <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl rounded-2xl shadow-md overflow-hidden">
                    <div className="text-center pt-8">
                        <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
                            Create Account
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

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-1">
                                    Username
                                </label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2.5 bg-zinc-100 dark:bg-zinc-800 
                                        border border-zinc-300 dark:border-zinc-600 text-sm
                                        text-zinc-900 dark:text-zinc-100 rounded-md 
                                        focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500
                                        focus:ring-1 focus:ring-zinc-400 dark:focus:ring-zinc-500
                                        disabled:opacity-50 disabled:cursor-not-allowed
                                        transition-all duration-200"
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-1">
                                        First Name
                                    </label>
                                    <input
                                        type="text"
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2.5 bg-zinc-100 dark:bg-zinc-800 
                                            border border-zinc-300 dark:border-zinc-600 text-sm
                                            text-zinc-900 dark:text-zinc-100 rounded-md 
                                            focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500
                                            focus:ring-1 focus:ring-zinc-400 dark:focus:ring-zinc-500
                                            disabled:opacity-50 disabled:cursor-not-allowed
                                            transition-all duration-200"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-1">
                                        Last Name
                                    </label>
                                    <input
                                        type="text"
                                        name="last_name"
                                        value={formData.last_name}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2.5 bg-zinc-100 dark:bg-zinc-800 
                                            border border-zinc-300 dark:border-zinc-600 text-sm
                                            text-zinc-900 dark:text-zinc-100 rounded-md 
                                            focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500
                                            focus:ring-1 focus:ring-zinc-400 dark:focus:ring-zinc-500
                                            disabled:opacity-50 disabled:cursor-not-allowed
                                            transition-all duration-200"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-1">
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2.5 bg-zinc-100 dark:bg-zinc-800 
                                        border border-zinc-300 dark:border-zinc-600 text-sm
                                        text-zinc-900 dark:text-zinc-100 rounded-md 
                                        focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500
                                        focus:ring-1 focus:ring-zinc-400 dark:focus:ring-zinc-500
                                        disabled:opacity-50 disabled:cursor-not-allowed
                                        transition-all duration-200"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-1">
                                    Password
                                </label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2.5 bg-zinc-100 dark:bg-zinc-800 
                                        border border-zinc-300 dark:border-zinc-600 text-sm
                                        text-zinc-900 dark:text-zinc-100 rounded-md 
                                        focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500
                                        focus:ring-1 focus:ring-zinc-400 dark:focus:ring-zinc-500
                                        disabled:opacity-50 disabled:cursor-not-allowed
                                        transition-all duration-200"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-zinc-700 dark:text-zinc-300 mb-1">
                                    Confirm Password
                                </label>
                                <input
                                    type="password"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2.5 bg-zinc-100 dark:bg-zinc-800 
                                        border border-zinc-300 dark:border-zinc-600 text-sm
                                        text-zinc-900 dark:text-zinc-100 rounded-md 
                                        focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-500
                                        focus:ring-1 focus:ring-zinc-400 dark:focus:ring-zinc-500
                                        disabled:opacity-50 disabled:cursor-not-allowed
                                        transition-all duration-200"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className={`w-full px-4 py-3 text-zinc-100 dark:text-zinc-900 
                                    font-medium bg-zinc-800 dark:bg-white rounded-md 
                                    hover:bg-zinc-700 dark:hover:bg-zinc-100 
                                    focus:outline-none focus:ring-2 focus:ring-zinc-900 
                                    dark:focus:ring-zinc-100 focus:ring-offset-2 
                                    focus:ring-offset-white dark:focus:ring-offset-zinc-900 
                                    transition-all duration-200 mt-6
                                    ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {loading ? (
                                    <div className="flex items-center justify-center font-medium">
                                        <svg className="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                                        </svg>
                                        Creating account...
                                    </div>
                                ) : 'Create Account'}
                            </button>
                        </form>

                        <div className="mt-6 text-center border-t border-zinc-200 dark:border-zinc-800 pt-6">
                            <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                Already have an account?{' '}
                                <Link to="/login" className="font-medium text-zinc-900 dark:text-zinc-100 hover:text-zinc-700 dark:hover:text-zinc-300">
                                    Sign in
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;