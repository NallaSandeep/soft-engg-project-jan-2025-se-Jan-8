import React from 'react';
import { NavLink } from 'react-router-dom';

const StudentNavigation = () => {
    return (
        <nav className="space-y-1">
            {/* Dashboard */}
            <NavLink
                to="/student/dashboard"
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

            {/* My Courses */}
            <NavLink
                to="/student/courses"
                className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                        isActive
                            ? 'bg-gray-100 text-blue-600'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                }
            >
                <svg className="mr-3 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
                </svg>
                My Courses
            </NavLink>

            {/* Assignments */}
            <NavLink
                to="/student/assignments"
                className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                        isActive
                            ? 'bg-gray-100 text-blue-600'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                }
            >
                <svg className="mr-3 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                    <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Assignments
            </NavLink>

            {/* Study Material */}
            <NavLink
                to="/student/materials"
                className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                        isActive
                            ? 'bg-gray-100 text-blue-600'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                }
            >
                <svg className="mr-3 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                </svg>
                Study Material
            </NavLink>
        </nav>
    );
};

export default StudentNavigation; 