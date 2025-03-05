import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userApi } from '../../services/apiService';
import { PencilSquareIcon, PlusCircleIcon, UserIcon } from '@heroicons/react/24/outline';

const UsersList = () => {
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        role: '',
        status: '',
        search: ''
    });
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchUsers();
    }, [filters]);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await userApi.getUsers(filters);
            if (response.success) {
                setUsers(response.data || []);
            } else {
                setError(response.message || 'Failed to load users');
            }
        } catch (err) {
            console.error('Error fetching users:', err);
            setError('Failed to load users');
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (name, value) => {
        setFilters(prev => ({ ...prev, [name]: value }));
    };

    const handleSearch = (e) => {
        e.preventDefault();
        handleFilterChange('search', searchTerm);
    };

    const filteredUsers = users.filter(user => {
        const matchesSearch = !filters.search || 
            user.first_name?.toLowerCase().includes(filters.search.toLowerCase()) ||
            user.last_name?.toLowerCase().includes(filters.search.toLowerCase()) ||
            user.email?.toLowerCase().includes(filters.search.toLowerCase()) ||
            user.username?.toLowerCase().includes(filters.search.toLowerCase());
        
        const matchesRole = !filters.role || user.role === filters.role;
        
        const matchesStatus = !filters.status || 
            (filters.status === 'active' && user.is_active) ||
            (filters.status === 'inactive' && !user.is_active);
        
        return matchesSearch && matchesRole && matchesStatus;
    });

    if (loading && users.length === 0) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Users</h1>
                <button
                    onClick={() => navigate('/admin/users/new')}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusCircleIcon className="h-5 w-5" />
                    <span>Add User</span>
                </button>
            </div>

            {/* Filters */}
            <div className="glass-card p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Role
                        </label>
                        <select
                            className="input-field"
                            value={filters.role}
                            onChange={(e) => handleFilterChange('role', e.target.value)}
                        >
                            <option value="">All Roles</option>
                            <option value="admin">Admin</option>
                            <option value="teacher">Teacher</option>
                            <option value="ta">Teaching Assistant</option>
                            <option value="student">Student</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Status
                        </label>
                        <select
                            className="input-field"
                            value={filters.status}
                            onChange={(e) => handleFilterChange('status', e.target.value)}
                        >
                            <option value="">All Status</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Search
                        </label>
                        <form onSubmit={handleSearch} className="flex">
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Search users..."
                                className="input-field rounded-r-none"
                            />
                            <button 
                                type="submit"
                                className="px-4 py-2 bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-200 rounded-r-lg hover:bg-zinc-300 dark:hover:bg-zinc-600"
                            >
                                Search
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            {/* Users Table */}
            <div className="glass-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-zinc-200 dark:divide-zinc-700">
                        <thead className="bg-zinc-50 dark:bg-zinc-800">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    User
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Email
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Role
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Status
                                </th>
                                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-zinc-900 divide-y divide-zinc-200 dark:divide-zinc-700">
                            {filteredUsers.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-4 text-center text-zinc-500 dark:text-zinc-400">
                                        No users found. Try adjusting your filters or add a new user.
                                    </td>
                                </tr>
                            ) : (
                                filteredUsers.map(user => (
                                    <tr key={user.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="flex-shrink-0 h-10 w-10 bg-zinc-200 dark:bg-zinc-700 rounded-full flex items-center justify-center">
                                                    <UserIcon className="h-6 w-6 text-zinc-500 dark:text-zinc-400" />
                                                </div>
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium text-zinc-900 dark:text-white">
                                                        {user.first_name} {user.last_name}
                                                    </div>
                                                    <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                                        {user.username}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                                {user.email}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                {
                                                    'admin': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
                                                    'teacher': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
                                                    'ta': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
                                                    'student': 'bg-zinc-100 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-300'
                                                }[user.role] || 'bg-zinc-100 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-300'
                                            }`}>
                                                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                user.is_active
                                                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                                            }`}>
                                                {user.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <button
                                                onClick={() => navigate(`/admin/users/${user.id}/edit`)}
                                                className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                                            >
                                                <PencilSquareIcon className="h-5 w-5" />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default UsersList; 