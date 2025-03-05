import React from 'react';
import { NavLink } from 'react-router-dom';

const AdminNavigation = () => {
    return (
        <nav className="space-y-1">
            {/* Dashboard */}
            <NavLink
                to="/admin/dashboard"
                className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                        isActive
                            ? 'bg-gray-100 text-blue-600'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                }
            >
                <svg className="mr-3 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
                Dashboard
            </NavLink>

            {/* Course Management Section */}
            <div className="border-t border-gray-200 pt-2">
                <h3 className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Course Management
                </h3>
                <div className="mt-1 space-y-1">
                    <NavLink
                        to="/admin/courses"
                        className={({ isActive }) =>
                            `flex items-center pl-8 pr-4 py-2 text-sm font-medium rounded-md ${
                                isActive
                                    ? 'bg-gray-100 text-blue-600'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`
                        }
                    >
                        Manage Courses
                    </NavLink>
                    <NavLink
                        to="/admin/lectures"
                        className={({ isActive }) =>
                            `flex items-center pl-8 pr-4 py-2 text-sm font-medium rounded-md ${
                                isActive
                                    ? 'bg-gray-100 text-blue-600'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`
                        }
                    >
                        Manage Lectures
                    </NavLink>
                    <NavLink
                        to="/admin/assignments"
                        className={({ isActive }) =>
                            `flex items-center pl-8 pr-4 py-2 text-sm font-medium rounded-md ${
                                isActive
                                    ? 'bg-gray-100 text-blue-600'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`
                        }
                    >
                        Manage Assignments
                    </NavLink>
                    <NavLink
                        to="/admin/question-bank"
                        className={({ isActive }) =>
                            `flex items-center pl-8 pr-4 py-2 text-sm font-medium rounded-md ${
                                isActive
                                    ? 'bg-gray-100 text-blue-600'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`
                        }
                    >
                        Question Bank
                    </NavLink>
                </div>
            </div>

            {/* User Management Section */}
            <div className="border-t border-gray-200 pt-2">
                <h3 className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    User Management
                </h3>
                <div className="mt-1 space-y-1">
                    <NavLink
                        to="/admin/students"
                        className={({ isActive }) =>
                            `flex items-center pl-8 pr-4 py-2 text-sm font-medium rounded-md ${
                                isActive
                                    ? 'bg-gray-100 text-blue-600'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`
                        }
                    >
                        Manage Students
                    </NavLink>
                    <NavLink
                        to="/admin/teaching-assistants"
                        className={({ isActive }) =>
                            `flex items-center pl-8 pr-4 py-2 text-sm font-medium rounded-md ${
                                isActive
                                    ? 'bg-gray-100 text-blue-600'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`
                        }
                    >
                        Teaching Assistants
                    </NavLink>
                </div>
            </div>

            {/* Reports & Logs Section */}
            <div className="border-t border-gray-200 pt-2">
                <h3 className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Analytics
                </h3>
                <div className="mt-1 space-y-1">
                    <NavLink
                        to="/admin/reports"
                        className={({ isActive }) =>
                            `flex items-center pl-8 pr-4 py-2 text-sm font-medium rounded-md ${
                                isActive
                                    ? 'bg-gray-100 text-blue-600'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`
                        }
                    >
                        Reports
                    </NavLink>
                    <NavLink
                        to="/admin/system-logs"
                        className={({ isActive }) =>
                            `flex items-center pl-8 pr-4 py-2 text-sm font-medium rounded-md ${
                                isActive
                                    ? 'bg-gray-100 text-blue-600'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`
                        }
                    >
                        System Logs
                    </NavLink>
                </div>
            </div>
        </nav>
    );
};

export default AdminNavigation; 