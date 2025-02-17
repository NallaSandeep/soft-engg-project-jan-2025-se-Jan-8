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
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
            <div className="w-full max-w-md">
                <Card variant="elevated" className="overflow-hidden">
                    <div className="px-8 py-6 bg-white">
                        <div className="text-center mb-6">
                            <h2 className="text-2xl font-bold text-gray-900">
                                Login to StudyHub
                            </h2>
                        </div>

                        {error && (
                            <div className="mb-6 p-3 text-sm text-red-600 bg-red-50 rounded-lg border border-red-100">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-4">
                                <Input
                                    type="email"
                                    label="Email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    disabled={loading}
                                    required
                                    fullWidth
                                    placeholder="Enter your email"
                                />

                                <Input
                                    type="password"
                                    label="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={loading}
                                    required
                                    fullWidth
                                    placeholder="Enter your password"
                                />
                            </div>

                            <Button
                                type="submit"
                                variant="primary"
                                disabled={loading}
                                loading={loading}
                                fullWidth
                            >
                                {loading ? 'Logging in...' : 'Login'}
                            </Button>

                            <div className="text-center text-sm text-gray-600">
                                <a 
                                    href="/forgot-password"
                                    className="hover:text-blue-600 transition-colors duration-200"
                                >
                                    Forgot your password?
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