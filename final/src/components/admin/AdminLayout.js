import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
    ChartBarIcon,
    UsersIcon,
    BookOpenIcon,
    ClipboardDocumentListIcon,
    QuestionMarkCircleIcon,
    Cog6ToothIcon
} from '@heroicons/react/24/outline';

const AdminLayout = () => {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const navLinks = [
        { to: '/admin/dashboard', icon: ChartBarIcon, text: 'Dashboard' },
        { to: '/admin/courses', icon: BookOpenIcon, text: 'Courses' },
        { to: '/admin/users', icon: UsersIcon, text: 'Users' },
        { to: '/admin/assignments', icon: ClipboardDocumentListIcon, text: 'Assignments' },
        { to: '/admin/question-bank', icon: QuestionMarkCircleIcon, text: 'Question Bank' },
        { to: '/admin/settings', icon: Cog6ToothIcon, text: 'Settings' }
    ];

       return (
        <div className="flex min-h-screen bg-zinc-100 dark:bg-zinc-900">
            <div className="fixed w-64 h-full bg-white/80 dark:bg-zinc-800/80 backdrop-blur-xl 
                          border-r border-zinc-200 dark:border-zinc-700">
                {/* Logo - add no-underline class */}
                <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                    <h1 className="text-xl font-bold text-zinc-900 dark:text-white no-underline">
                        StudyHub Admin
                    </h1>
                </div>

                {/* Navigation - updated with custom underline animation */}
                <nav className="p-4 space-y-2">
                    {navLinks.map((link) => (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            className={({ isActive }) =>
                                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all
                                relative no-underline
                                ${isActive
                                    ? 'bg-zinc-800 dark:bg-white text-white dark:text-zinc-900'
                                    : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-700/50'
                                }
                                after:absolute after:bottom-0 after:left-0 after:h-0.5 
                                after:w-full after:origin-bottom-left
                                after:scale-x-0 hover:after:scale-x-100
                                after:transition-transform after:duration-300
                                ${isActive 
                                    ? 'after:bg-white dark:after:bg-zinc-900 after:scale-x-100' 
                                    : 'after:bg-zinc-600 dark:after:bg-zinc-400'
                                }`
                            }
                        >
                            <link.icon className="h-5 w-5" />
                            <span className="font-medium">{link.text}</span>
                        </NavLink>
                    ))}
                </nav>

                {/* Logout Button */}
                <div className="absolute bottom-0 left-0 right-0 p-4">
                    <button
                        onClick={handleLogout}
                        className="w-full px-4 py-3 flex items-center justify-center space-x-2
                                 text-zinc-600 dark:text-zinc-400 font-medium
                                 hover:bg-zinc-100 dark:hover:bg-zinc-700/50
                                 rounded-lg transition-all"
                    >
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        <span>Sign out</span>
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 ml-64">
                <main className="p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default AdminLayout;