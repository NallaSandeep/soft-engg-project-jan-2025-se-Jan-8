import React from 'react';
import { NavLink } from 'react-router-dom';

const TANavigation = () => {
    return (
        <nav className="space-y-1">
            {/* Dashboard */}
            <NavLink
                to="/ta/dashboard"
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
                        to="/ta/lectures"
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
                        to="/ta/assignments"
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
                        to="/ta/question-bank"
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

            {/* System Logs Section */}
            <div className="border-t border-gray-200 pt-2">
                <h3 className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    System
                </h3>
                <div className="mt-1 space-y-1">
                    <NavLink
                        to="/ta/system-logs"
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

export default TANavigation; 