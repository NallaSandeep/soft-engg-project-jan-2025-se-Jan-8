import React from 'react';
import { Link, NavLink, useNavigate  } from 'react-router-dom';

const Navbar = () => {
    // Placeholder user data (No API calls)
    const user = {
        role: 'student', // Change to 'admin' or 'ta' for testing
        first_name: 'John',
        last_name: 'Doe'
    };
    const navigate = useNavigate();
    const logout = () => {
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');

        // Redirect to login page
        navigate('/login');
    };

    const getNavLinks = () => {
        switch (user.role) {
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
                    { to: '/student/assignments', text: 'Assignments' },
                    { to: '/knowledge-base', text: 'Knowledge Base' }
                ];
            default:
                return [];
        }
    };

    return (
        <nav className="bg-gray-900 border-b border-yellow-500 shadow-lg">
            <div className="w-full px-4">
                <div className="flex justify-between h-16 items-center">
                    {/* Logo */}
                    <div className="flex items-center space-x-8">
                        <Link to="/" className="text-xl font-bold text-yellow-400 hover:text-yellow-300 transition-colors">
                            StudyHub
                        </Link>

                        {/* Desktop Navigation */}
                        <div className="hidden md:flex space-x-4">
                            {getNavLinks().map((link) => (
                                <NavLink
                                    key={link.to}
                                    to={link.to}
                                    className={({ isActive }) =>
                                        `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                            isActive
                                                ? 'bg-yellow-500 text-black'
                                                : 'text-gray-300 hover:bg-gray-800 hover:text-yellow-400'
                                        }`
                                    }
                                >
                                    {link.text}
                                </NavLink>
                            ))}
                        </div>
                    </div>

                    {/* User Info & Logout */}
                    <div className="flex items-center space-x-4">
                        <span className="text-yellow-400">
                            {user.role === 'student' ? 'Welcome, Student' : `Welcome, ${user.first_name} ${user.last_name}`}
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
            <div className="md:hidden bg-gray-800 border-t border-yellow-500">
                <div className="px-2 pt-2 pb-3 space-y-1">
                    {getNavLinks().map((link) => (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            className={({ isActive }) =>
                                `block px-3 py-2 rounded-md text-base font-medium ${
                                    isActive
                                        ? 'bg-yellow-500 text-black'
                                        : 'text-gray-300 hover:bg-gray-700 hover:text-yellow-400'
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
