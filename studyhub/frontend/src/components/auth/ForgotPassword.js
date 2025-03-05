import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Card } from '../common/Card';
import { Button } from '../common/Button';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { resetPassword } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        setLoading(true);

        try {
            const result = await resetPassword(email);
            if (result.success) {
                setMessage('Password reset instructions have been sent to your email.');
            } else {
                setError(result.error || 'Failed to send reset email');
            }
        } catch (err) {
            console.error('Reset password error:', err);
            setError(err.message || 'An error occurred. Please try again.');
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
                                Reset Your Password
                            </h2>
                            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                                Enter your email address and we'll send you instructions to reset your password.
                            </p>
                        </div>

                        {error && (
                            <div className="mb-6 p-3 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-800">
                                {error}
                            </div>
                        )}

                        {message && (
                            <div className="mb-6 p-3 text-sm text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-100 dark:border-green-800">
                                {message}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    disabled={loading}
                                    required
                                    placeholder="Enter your email"
                                    className="appearance-none block w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                />
                            </div>

                            <Button
                                type="submit"
                                variant="primary"
                                disabled={loading}
                                loading={loading}
                                fullWidth
                                className="bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600"
                            >
                                {loading ? 'Sending...' : 'Send Reset Instructions'}
                            </Button>

                            <div className="text-center text-sm text-zinc-600 dark:text-zinc-400">
                                <Link 
                                    to="/login"
                                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                                >
                                    Back to Login
                                </Link>
                            </div>
                        </form>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default ForgotPassword; 