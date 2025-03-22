import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import ThemeToggle from '../themeToggle/ThemeToggle';
import { 
    UserCircleIcon,
    AcademicCapIcon,
    BookOpenIcon,
    ClipboardDocumentListIcon,
    ChartBarIcon,
    UsersIcon,
    Cog6ToothIcon
} from '@heroicons/react/24/outline';

const Navbar = () => {
    const { user, logout } = useAuth();

    const getDashboardPath = () => {
        switch (user?.role) {
            case 'admin':
                return '/admin/dashboard';
            case 'ta':
                return '/ta/dashboard';
            case 'student':
            default:
                return '/student/dashboard';
        }
    };

    const getNavLinks = () => {
        switch (user?.role) {
            case 'admin':
                return [
                    { to: '/admin/dashboard', text: 'Dashboard', icon: ChartBarIcon },
                    { to: '/admin/users', text: 'Users', icon: UsersIcon },
                    { to: '/admin/courses', text: 'Courses', icon: BookOpenIcon }
                ];
            case 'ta':
                return [
                    { to: '/ta/dashboard', text: 'Dashboard', icon: ChartBarIcon },
                    { to: '/ta/courses', text: 'My Courses', icon: BookOpenIcon },
                    { to: '/ta/assignments', text: 'Grade Assignments', icon: ClipboardDocumentListIcon }
                ];
            case 'student':
                return [
                    { to: '/student/dashboard', text: 'Dashboard', icon: ChartBarIcon },
                    { to: '/student/courses', text: 'My Courses', icon: BookOpenIcon },
                    { to: '/student/assignments', text: 'Assignments', icon: ClipboardDocumentListIcon },
                    { to: '/personal-resources', text: 'Personal Resources', icon: AcademicCapIcon }
                ];
            default:
                return [];
        }
    };

    const getRoleLabel = () => {
        switch (user?.role) {
            case 'admin':
                return 'Administrator';
            case 'ta':
                return 'Teaching Assistant';
            case 'student':
                return 'Student';
            default:
                return 'User';
        }
    };

    return (
        <nav className="bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm border-b border-zinc-200 dark:border-zinc-700 sticky top-0 z-10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center space-x-8">
                        <Link to={getDashboardPath()} className="flex items-center text-xl font-bold text-zinc-900 dark:text-white">
                            <AcademicCapIcon className="h-8 w-8 mr-2" />
                            StudyHub
                        </Link>

                        {/* Navigation Links */}
                        <div className="hidden md:flex space-x-2">
                            {getNavLinks().map((link) => (
                                <NavLink
                                    key={link.to}
                                    to={link.to}
                                    className={({ isActive }) =>
                                        `nav-link ${isActive ? 'active' : ''}`
                                    }
                                >
                                    <link.icon className="h-5 w-5 mr-2" />
                                    {link.text}
                                </NavLink>
                            ))}
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* Theme Toggle */}
                        <ThemeToggle />

                        {/* User Menu */}
                        <div className="relative">
                            <div className="flex items-center space-x-2 text-zinc-700 dark:text-zinc-300 cursor-pointer">
                                <UserCircleIcon className="h-8 w-8" />
                                <div className="hidden md:block">
                                    <div className="text-sm font-medium">{user?.email}</div>
                                    <div className="text-xs text-zinc-500 dark:text-zinc-400">{getRoleLabel()}</div>
                                </div>
                            </div>
                        </div>

                        {/* Logout Button */}
                        <button
                            onClick={logout}
                            className="px-3 py-2 text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-white"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar; 