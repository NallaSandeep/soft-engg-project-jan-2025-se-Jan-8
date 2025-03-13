import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { userApi } from '../../services/apiService';
import { toast } from 'react-hot-toast';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const UserForm = () => {
    const navigate = useNavigate();
    const { userId } = useParams();
    const isEditMode = Boolean(userId);

    const [loading, setLoading] = useState(isEditMode);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        role: 'student',
        is_active: true
    });

    useEffect(() => {
        if (isEditMode) {
            fetchUser();
        }
    }, [userId]);

    const fetchUser = async () => {
        try {
            const response = await userApi.getUser(userId);
            if (response.user.id != undefined) {
                const user = response.user;
                setFormData({
                    username: user.username,
                    email: user.email,
                    password: '', // Don't populate password in edit mode
                    first_name: user.first_name,
                    last_name: user.last_name,
                    role: user.role,
                    is_active: user.is_active
                });
            } else {
                setError(response.message || 'Failed to load user');
            }
        } catch (err) {
            console.error('Error fetching user:', err);
            setError('Failed to load user');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            setLoading(true);
            setError(null);
            
            let response;
            if (isEditMode) {
                // For edit mode, only send password if it's been changed
                const userData = { ...formData };
                if (!userData.password) {
                    delete userData.password;
                }
                response = await userApi.updateUser(userId, userData);
            } else {
                response = await userApi.createUser(formData);
            }
            
            if (response.success) {
                toast.success(`User ${isEditMode ? 'updated' : 'created'} successfully!`);
                navigate('/admin/users');
            } else {
                setError(response.message || `Failed to ${isEditMode ? 'update' : 'create'} user`);
            }
        } catch (err) {
            console.error(`Error ${isEditMode ? 'updating' : 'creating'} user:`, err);
            setError(err.message || `Failed to ${isEditMode ? 'update' : 'create'} user`);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>
        );
    }

    return (
        <div>
            <div className="max-w-3xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                        {isEditMode ? 'Edit User' : 'Create User'}
                    </h1>
                    <button
                        onClick={() => navigate('/admin/users')}
                        className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200 flex items-center gap-1"
                    >
                        <ArrowLeftIcon className="h-4 w-4" /> Back to Users
                    </button>
                </div>

                {error && (
                    <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="glass-card p-6">
                        <div className="grid grid-cols-1 gap-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        First Name
                                    </label>
                                    <input
                                        type="text"
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleChange}
                                        className="input-field"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        Last Name
                                    </label>
                                    <input
                                        type="text"
                                        name="last_name"
                                        value={formData.last_name}
                                        onChange={handleChange}
                                        className="input-field"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Username
                                </label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    className="input-field"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Email
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="input-field"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Password {isEditMode && <span className="text-zinc-500 dark:text-zinc-400 text-xs">(Leave blank to keep current password)</span>}
                                </label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="input-field"
                                    {...(!isEditMode && { required: true })}
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        Role
                                    </label>
                                    <select
                                        name="role"
                                        value={formData.role}
                                        onChange={handleChange}
                                        className="input-field"
                                        required
                                    >
                                        <option value="student">Student</option>
                                        <option value="teacher">Teacher</option>
                                        <option value="ta">Teaching Assistant</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>

                                <div className="flex items-center h-full pt-6">
                                    <label className="flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            name="is_active"
                                            checked={formData.is_active}
                                            onChange={handleChange}
                                            className="h-4 w-4 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400 rounded"
                                        />
                                        <span className="ml-2 text-sm text-zinc-700 dark:text-zinc-300">
                                            Active Account
                                        </span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end space-x-4">
                        <button
                            type="button"
                            onClick={() => navigate('/admin/users')}
                            className="px-4 py-2 border border-zinc-300 dark:border-zinc-600 text-zinc-700 dark:text-zinc-300 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                        >
                            {isEditMode ? 'Update' : 'Create'} User
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default UserForm; 