import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const Navbar = () => {
    const { user, logout } = useAuth();

    const getNavLinks = () => {
        switch (user?.role) {
            case 'admin':
                return [
                    { to: '/admin/dashboard', text: 'Dashboard' },
                    { to: '/admin/users', text: 'Users' },
                    { to: '/admin/courses', text: 'Courses' }
                ];
            case 'ta':
                return [
                    { to: '/ta/dashboard', text: 'Dashboard' },
                    { to: '/ta/courses', text: 'My Courses' },
                    { to: '/ta/grading', text: 'Grade Assignments' }
                ];
            case 'student':
                return [
                    { to: '/student/dashboard', text: 'Dashboard' },
                    { to: '/student/courses', text: 'My Courses' },
                    { to: '/student/assignments', text: 'Assignments' }
                ];
            default:
                return [];
        }
    };

    return (
        <nav className="bg-white border-b border-gray-200">
            <div className="w-full px-4">
                <div className="flex justify-between h-16">
                    <div className="flex items-center space-x-8">
                        <Link to="/" className="text-xl font-bold text-blue-600">
                            StudyHub
                        </Link>

                        {/* Navigation Links */}
                        <div className="hidden md:flex space-x-4">
                            {getNavLinks().map((link) => (
                                <NavLink
                                    key={link.to}
                                    to={link.to}
                                    className={({ isActive }) =>
                                        `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                            isActive
                                                ? 'bg-blue-50 text-blue-600'
                                                : 'text-gray-600 hover:bg-gray-50'
                                        }`
                                    }
                                >
                                    {link.text}
                                </NavLink>
                            ))}
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* User Info & Logout */}
                        <span className="text-gray-700">
                            Welcome, {user?.first_name} {user?.last_name}
                        </span>
                        <button
                            onClick={logout}
                            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation */}
            <div className="md:hidden">
                <div className="px-2 pt-2 pb-3 space-y-1">
                    {getNavLinks().map((link) => (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            className={({ isActive }) =>
                                `block px-3 py-2 rounded-md text-base font-medium ${
                                    isActive
                                        ? 'bg-blue-50 text-blue-600'
                                        : 'text-gray-600 hover:bg-gray-50'
                                }`
                            }
                        >
                            {link.text}
                        </NavLink>
                    ))}
                </div>
            </div>
        </nav>
    );
};

export default Navbar; 