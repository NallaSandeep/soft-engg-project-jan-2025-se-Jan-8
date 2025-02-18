import React from 'react';
import { NavLink } from 'react-router-dom';

const StudentNavigation = () => {
    return (
        <nav className="space-y-2">
            {/* Dashboard */}
            <NavLink
                to="/student/dashboard"
                className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md transition ${
                        isActive
                            ? 'bg-gray-800 text-warning'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-warning'
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
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md transition ${
                        isActive
                            ? 'bg-gray-800 text-warning'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-warning'
                    }`
                }
            >
                <svg className="mr-3 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3z" />
                </svg>
                My Courses
            </NavLink>

            {/* Assignments */}
            <NavLink
                to="/student/assignments"
                className={({ isActive }) =>
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md transition ${
                        isActive
                            ? 'bg-gray-800 text-warning'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-warning'
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
                    `flex items-center px-4 py-2 text-sm font-medium rounded-md transition ${
                        isActive
                            ? 'bg-gray-800 text-warning'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-warning'
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
