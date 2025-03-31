import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Card } from '../common/Card';
import { Button } from '../common/Button';

const Register = () => {
    const { register } = useAuth();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
        role: 'student'
    });
    const [error, setError] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (error) setError(null);
        if (successMsg) {
            setSuccessMsg(null);
        }
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

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        setLoading(true);
        setError(null);
        setSuccessMsg(null);

        try {
            const result = await register({
                username: formData.username,
                email: formData.email,
                password: formData.password,
                first_name: formData.first_name,
                last_name: formData.last_name,
                role: formData.role
            });
            if (!result.success) {
                setError(result.error);
            } else {
                setFormData({
                    username: '',
                    email: '',
                    password: '',
                    confirmPassword: '',
                    first_name: '',
                    last_name: '',
                    role: 'student'
                });
                setSuccessMsg('Registration successful. Please go to login page to sign in.');
            }
        } catch (err) {
            setError(err.message || 'An error occurred during registration');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <h2 className="mt-6 text-center text-3xl font-extrabold text-zinc-900 dark:text-white">
                    Create your account
                </h2>
                <p className="mt-2 text-center text-sm text-zinc-600 dark:text-zinc-400">
                    Or{' '}
                    <Link to="/login" className="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300">
                        sign in to your existing account
                    </Link>
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                <Card className="py-8 px-4 sm:px-10">
                    {error && (
                        <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded relative mb-4" role="alert">
                            <span className="block sm:inline">{error}</span>
                        </div>
                    )}

                    {successMsg && (
                        <div className="bg-green-100 dark:bg-green-900/20 border border-green-400 dark:border-green-800 text-green-700 dark:text-green-400 px-4 py-3 rounded relative mb-4" role="alert">
                            <span className="block sm:inline">{successMsg}</span>
                        </div>
                    )}

                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div>
                            <label htmlFor="role" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                Role
                            </label>
                            <div className="mt-1">
                                <select
                                    id="role"
                                    name="role"
                                    autoComplete="role"
                                    required
                                    value={formData.role}
                                    onChange={handleInputChange}
                                    className="appearance-none block w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                >
                                    <option value="student">Student</option>
                                    <option value="ta">Teaching Assistant</option>
                                </select>
                            </div>
                        </div>
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                Username
                            </label>
                            <div className="mt-1">
                                <input
                                    id="username"
                                    name="username"
                                    type="text"
                                    autoComplete="username"
                                    required
                                    value={formData.username}
                                    onChange={handleInputChange}
                                    className="appearance-none block w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                Email address
                            </label>
                            <div className="mt-1">
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    required
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    className="appearance-none block w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="first_name" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                First Name
                            </label>
                            <div className="mt-1">
                                <input
                                    id="first_name"
                                    name="first_name"
                                    type="text"
                                    autoComplete="given-name"
                                    required
                                    value={formData.first_name}
                                    onChange={handleInputChange}
                                    className="appearance-none block w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="last_name" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                Last Name
                            </label>
                            <div className="mt-1">
                                <input
                                    id="last_name"
                                    name="last_name"
                                    type="text"
                                    autoComplete="family-name"
                                    required
                                    value={formData.last_name}
                                    onChange={handleInputChange}
                                    className="appearance-none block w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                Password
                            </label>
                            <div className="mt-1">
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="new-password"
                                    required
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    className="appearance-none block w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                Confirm Password
                            </label>
                            <div className="mt-1">
                                <input
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    type="password"
                                    autoComplete="new-password"
                                    required
                                    value={formData.confirmPassword}
                                    onChange={handleInputChange}
                                    className="appearance-none block w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                />
                            </div>
                        </div>

                        <div>
                            <Button
                                type="submit"
                                variant="primary"
                                disabled={loading}
                                loading={loading}
                                fullWidth
                                className="bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600"
                            >
                                {loading ? 'Creating account...' : 'Create account'}
                            </Button>
                        </div>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default Register; 