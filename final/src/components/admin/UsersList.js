import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
    PencilSquareIcon,
    TrashIcon,
    PlusIcon,
    UserGroupIcon,
    MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

const UsersList = () => {
    const navigate = useNavigate();
    const [filters, setFilters] = useState({ role: "", status: "", search: "" });

    // Mock user data
    const users = [
        { id: 1, first_name: "Alice", last_name: "Admin", email: "alice@example.com", role: "admin", is_active: true },
        { id: 2, first_name: "Bob", last_name: "Student", email: "bob@example.com", role: "student", is_active: false },
        { id: 3, first_name: "Charlie", last_name: "TA", email: "charlie@example.com", role: "ta", is_active: true }
    ];

    const handleFilterChange = (name, value) => {
        setFilters(prev => ({ ...prev, [name]: value }));
    };

    const filteredUsers = users.filter(user => {
        if (filters.role && user.role !== filters.role) return false;
        if (filters.status) {
            const isActive = filters.status === "active";
            if (user.is_active !== isActive) return false;
        }
        if (filters.search) {
            const searchTerm = filters.search.toLowerCase();
            return (
                user.first_name.toLowerCase().includes(searchTerm) ||
                user.last_name.toLowerCase().includes(searchTerm) ||
                user.email.toLowerCase().includes(searchTerm)
            );
        }
        return true;
    });

    const handleDelete = (userId) => {
        if (window.confirm("Are you sure you want to delete this user?")) {
            console.log("User deleted:", userId);
        }
    };

    return (
        <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900">
            <div className="max-w-7xl mx-auto space-y-8 p-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
                            Users
                        </h1>
                        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                            Manage platform users
                        </p>
                    </div>
                    <button
                        onClick={() => navigate('/admin/users/new')}
                        className="flex items-center space-x-2 px-4 py-2 rounded-lg
                                 bg-zinc-800 dark:bg-white
                                 text-white dark:text-zinc-900
                                 hover:bg-zinc-700 dark:hover:bg-zinc-100
                                 transition-colors duration-200"
                    >
                        <PlusIcon className="h-5 w-5" />
                        <span>Add User</span>
                    </button>
                </div>

                {/* Filters */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl p-6
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                                Role
                            </label>
                            <select
                                value={filters.role}
                                onChange={(e) => handleFilterChange("role", e.target.value)}
                                className="w-full rounded-lg border border-zinc-200 dark:border-zinc-700
                                         bg-white dark:bg-zinc-800 px-4 py-2
                                         text-zinc-900 dark:text-white
                                         focus:outline-none focus:ring-2 focus:ring-zinc-500"
                            >
                                <option value="">All Roles</option>
                                <option value="admin">Admin</option>
                                <option value="teacher">Teacher</option>
                                <option value="TA">Teaching Assistant</option>
                                <option value="student">Student</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                                Status
                            </label>
                            <select
                                value={filters.status}
                                onChange={(e) => handleFilterChange("status", e.target.value)}
                                className="w-full rounded-lg border border-zinc-200 dark:border-zinc-700
                                         bg-white dark:bg-zinc-800 px-4 py-2
                                         text-zinc-900 dark:text-white
                                         focus:outline-none focus:ring-2 focus:ring-zinc-500"
                            >
                                <option value="">All Status</option>
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                                Search
                            </label>
                            <div className="relative">
                                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-zinc-400" />
                                <input
                                    type="text"
                                    placeholder="Search users..."
                                    value={filters.search}
                                    onChange={(e) => handleFilterChange("search", e.target.value)}
                                    className="w-full rounded-lg border border-zinc-200 dark:border-zinc-700
                                             bg-white dark:bg-zinc-800 pl-10 pr-4 py-2
                                             text-zinc-900 dark:text-white
                                             focus:outline-none focus:ring-2 focus:ring-zinc-500"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Users Table */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-zinc-200 dark:border-zinc-700">
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Name</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Email</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Role</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Status</th>
                                    <th className="text-right p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredUsers.map(user => (
                                    <tr
                                        key={user.id}
                                        className="border-b border-zinc-200 dark:border-zinc-700 last:border-0
                                                 hover:bg-zinc-50 dark:hover:bg-zinc-800/50
                                                 transition-colors duration-200"
                                    >
                                        <td className="p-4">
                                            <div className="flex items-center space-x-3">
                                                <UserGroupIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500" />
                                                <span className="font-medium text-zinc-900 dark:text-white">
                                                    {user.first_name} {user.last_name}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="p-4 text-zinc-600 dark:text-zinc-400">
                                            {user.email}
                                        </td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                                ${user.role === 'admin' 
                                                    ? 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-100'
                                                    : user.role === 'student'
                                                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                                                    : 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                                                }`}
                                            >
                                                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                                ${user.is_active
                                                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-800 dark:text-emerald-100'
                                                    : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                                                }`}
                                            >
                                                {user.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right">
                                            <div className="flex justify-end space-x-2">
                                                <button
                                                    onClick={() => navigate(`/admin/users/${user.id}/edit`)}
                                                    className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-700
                                                             text-zinc-600 dark:text-zinc-400
                                                             transition-colors duration-200"
                                                >
                                                    <PencilSquareIcon className="h-5 w-5" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(user.id)}
                                                    className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20
                                                             text-red-600 dark:text-red-400
                                                             transition-colors duration-200"
                                                >
                                                    <TrashIcon className="h-5 w-5" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UsersList;