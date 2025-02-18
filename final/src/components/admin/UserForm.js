import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const UserForm = () => {
    const navigate = useNavigate();
    const { userId } = useParams();
    const isEditMode = Boolean(userId);

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        role: 'student',
        is_active: true
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Form Submitted:', formData);
        navigate('/admin/users'); // Redirect after submission
    };

    return (
        <div className="p-6 bg-black min-h-screen text-white">
            <div className="max-w-3xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-yellow-400">
                        {isEditMode ? 'Edit User' : 'Create User'}
                    </h1>
                    <button
                        onClick={() => navigate('/admin/users')}
                        className="text-gray-400 hover:text-gray-200 transition"
                    >
                        Cancel
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="bg-gray-950 rounded-lg shadow-lg p-6">
                        <div className="grid grid-cols-1 gap-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-1">
                                        First Name
                                    </label>
                                    <input
                                        type="text"
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleChange}
                                        className="w-full border border-gray-800 bg-black text-white rounded-lg px-3 py-2 focus:ring-yellow-400 focus:border-yellow-400"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-1">
                                        Last Name
                                    </label>
                                    <input
                                        type="text"
                                        name="last_name"
                                        value={formData.last_name}
                                        onChange={handleChange}
                                        className="w-full border border-gray-800 bg-black text-white rounded-lg px-3 py-2 focus:ring-yellow-400 focus:border-yellow-400"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">
                                    Username
                                </label>
                                <input
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    className="w-full border border-gray-800 bg-black text-white rounded-lg px-3 py-2 focus:ring-yellow-400 focus:border-yellow-400"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">
                                    Email
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full border border-gray-800 bg-black text-white rounded-lg px-3 py-2 focus:ring-yellow-400 focus:border-yellow-400"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">
                                    Password {isEditMode && '(leave blank to keep unchanged)'}
                                </label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full border border-gray-800 bg-black text-white rounded-lg px-3 py-2 focus:ring-yellow-400 focus:border-yellow-400"
                                    required={!isEditMode}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">
                                    Role
                                </label>
                                <select
                                    name="role"
                                    value={formData.role}
                                    onChange={handleChange}
                                    className="w-full border border-gray-800 bg-black text-white rounded-lg px-3 py-2 focus:ring-yellow-400 focus:border-yellow-400"
                                >
                                    <option value="student">Student</option>
                                    <option value="admin">Admin</option>
                                    <option value="ta">TA</option>
                                </select>
                            </div>

                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleChange}
                                    className="h-4 w-4 text-yellow-400 border-gray-800 rounded bg-black"
                                />
                                <label className="ml-2 text-sm text-gray-300">
                                    User is active
                                </label>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end space-x-4">
                        <button
                            type="button"
                            onClick={() => navigate('/admin/users')}
                            className="px-4 py-2 border border-gray-800 text-gray-300 rounded-lg hover:bg-gray-800 transition"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-yellow-400 text-black font-bold rounded-lg hover:bg-yellow-500 transition"
                        >
                            {isEditMode ? 'Update User' : 'Create User'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default UserForm;
