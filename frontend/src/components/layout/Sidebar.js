import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const Sidebar = () => {
    const { user } = useAuth();

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
        <aside className="w-64 bg-white shadow-lg min-h-screen">
            <div className="p-4">
                <nav className="space-y-1">
                    {getNavLinks().map((link) => (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            className={({ isActive }) =>
                                `block px-4 py-2 rounded-lg transition-colors ${
                                    isActive
                                        ? 'bg-blue-50 text-blue-700'
                                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`
                            }
                        >
                            {link.text}
                        </NavLink>
                    ))}
                </nav>
            </div>
        </aside>
    );
};

export default Sidebar; 