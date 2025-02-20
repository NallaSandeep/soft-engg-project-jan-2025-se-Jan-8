import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const Navigation = () => {
    const { user } = useAuth();
    console.log(user);

    const adminLinks = [
        { to: '/admin/users', text: 'Users', icon: 'users' },
        { to: '/admin/courses', text: 'Courses', icon: 'book' },
        { to: '/admin/assignments', text: 'Assignments', icon: 'clipboard' },
        { to: '/admin/resources', text: 'Resources', icon: 'folder' }
    ];

    const taLinks = [
        { to: '/ta/dashboard', text: 'Dashboard', icon: 'home' },
        { to: '/ta/courses', text: 'My Courses', icon: 'book' },
        { to: '/ta/assignments', text: 'Assignments', icon: 'clipboard' },
        { to: '/ta/grades', text: 'Grading', icon: 'check-square' }
    ];

    const studentLinks = [
        { to: '/student/dashboard', text: 'Dashboard', icon: 'home' },
        { to: '/student/courses', text: 'My Courses', icon: 'book' },
        { to: '/student/assignments', text: 'Assignments', icon: 'clipboard' },
        { to: '/student/resources', text: 'Resources', icon: 'folder' },
        { to: '/student/progress', text: 'Progress', icon: 'chart-line' }
    ];

    const getNavLinks = () => {
        switch (user?.role) {
            case 'admin':
                return adminLinks;
            case 'ta':
                return taLinks;
            case 'student':
                return studentLinks;
            default:
                return [];
        }
    };

    const getIcon = (iconName) => {
        switch (iconName) {
            case 'users':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                );
            case 'book':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                );
            case 'clipboard':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                );
            case 'folder':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                );
            case 'check-square':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                );
            case 'home':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                );
            case 'chart-line':
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                    </svg>
                );
            default:
                return null;
        }
    };

    return (
        <nav className="space-y-1">
            {getNavLinks().map(link => (
                <NavLink
                    key={link.to}
                    to={link.to}
                    className={({ isActive }) =>
                        `flex items-center px-4 py-2 text-sm font-medium ${
                            isActive
                                ? 'bg-gray-100 text-blue-600'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`
                    }
                >
                    <span className="mr-3">{getIcon(link.icon)}</span>
                    {link.text}
                </NavLink>
            ))}
        </nav>
    );
};

export default Navigation; 