import React, { useState, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
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
    const [user, setUser] = useState(null);
    const navigate = useNavigate();
    
    useEffect(() => {
        const storedUser = sessionStorage.getItem('userRole');
        console.log(storedUser);
        if (storedUser) {
            setUser(storedUser);
        } else {
            navigate('/login');
        }
    }, [navigate]);

    const logout = () => {
        sessionStorage.removeItem('user');
        navigate('/login');
    };

    const getNavLinks = () => {
        if (!user) return [];

        switch (user) {
            case 'admin':
                return [
                    { 
                        to: '/admin/dashboard', 
                        text: 'Dashboard',
                        icon: ChartBarIcon 
                    },
                    { 
                        to: '/admin/users', 
                        text: 'Users',
                        icon: UsersIcon 
                    },
                    { 
                        to: '/admin/courses', 
                        text: 'Courses',
                        icon: BookOpenIcon 
                    },
                    { 
                        to: '/admin/settings', 
                        text: 'Settings',
                        icon: Cog6ToothIcon 
                    }
                ];
            case 'ta':
                return [
                    { 
                        to: '/ta/dashboard', 
                        text: 'Dashboard',
                        icon: ChartBarIcon 
                    },
                    { 
                        to: '/ta/courses', 
                        text: 'My Courses',
                        icon: BookOpenIcon 
                    },
                    { 
                        to: '/ta/assignments', 
                        text: 'Grade Assignments',
                        icon: ClipboardDocumentListIcon 
                    }
                ];
            case 'student':
                return [
                    { 
                        to: '/student/dashboard', 
                        text: 'Dashboard',
                        icon: ChartBarIcon 
                    },
                    { 
                        to: '/student/courses', 
                        text: 'My Courses',
                        icon: BookOpenIcon 
                    },
                    { 
                        to: '/student/assignments', 
                        text: 'Assignments',
                        icon: ClipboardDocumentListIcon 
                    }
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
                return '';
        }
    };

    if (!user) {
        return <div className="h-16 bg-zinc-100 dark:bg-zinc-900"></div>;
    }

    return (
        <nav className="sticky top-0 z-20 bg-zinc-100 dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16 items-center">
                    {/* Logo */}
                    <div className="flex items-center space-x-8">
                        <Link to={`/${user.role}/dashboard`} 
                              className="flex items-center space-x-2 text-xl font-bold text-zinc-900 dark:text-white no-underline">
                            <AcademicCapIcon className="h-8 w-8" />
                            <span>StudyHub</span>
                        </Link>

                        {/* Desktop Navigation */}
                        <div className="hidden md:flex space-x-6">
                            {getNavLinks().map((link) => (
                                <NavLink
                                    key={link.to}
                                    to={link.to}
                                    className={({ isActive }) =>
                                        `flex items-center space-x-2 px-1 py-2 text-sm font-medium 
                                        transition-all duration-200 relative
                                        ${isActive 
                                            ? 'text-zinc-900 dark:text-white' 
                                            : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                                        }
                                        after:absolute after:bottom-0 after:left-0 after:h-0.5 
                                        after:w-full after:bg-zinc-900 after:dark:bg-white 
                                        after:transform after:origin-bottom-left
                                        after:transition-transform after:duration-200
                                        ${isActive ? 'after:scale-x-100' : 'after:scale-x-0 hover:after:scale-x-100'} 
                                        no-underline`
                                    }
                                >
                                    <link.icon className="h-4 w-4" />
                                    <span>{link.text}</span>
                                </NavLink>
                            ))}
                        </div>
                    </div>

                    {/* User Info & Actions */}
                    <div className="flex items-center space-x-6">
                        <div className="flex flex-col items-end">
                            <span className="text-sm font-medium text-zinc-900 dark:text-white">
                               Welcome back, {user?.first_name || user?.username || 'User'} 
                            </span>
                            <span className="text-xs text-zinc-600 dark:text-zinc-400">
                                {getRoleLabel()}
                            </span>
                        </div>
                        <ThemeToggle />
                        <button
                            onClick={logout}
                            className="px-4 py-2 text-sm font-medium bg-zinc-100 dark:bg-zinc-800 
                                     text-zinc-900 dark:text-white rounded-lg
                                     hover:bg-zinc-200 dark:hover:bg-zinc-700 
                                     transition-colors duration-200"
                        >
                            Sign out
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation */}
            <div className="md:hidden border-t border-zinc-200 dark:border-zinc-800">
                <div className="px-2 py-3 space-y-1">
                    {getNavLinks().map((link) => (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            className={({ isActive }) =>
                                `flex items-center space-x-3 px-3 py-2 text-base font-medium 
                                transition-all duration-200
                                ${isActive 
                                    ? 'text-zinc-900 dark:text-white bg-zinc-200 dark:bg-zinc-800 rounded-lg' 
                                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                                }`
                            }
                        >
                            <link.icon className="h-5 w-5" />
                            <span>{link.text}</span>
                        </NavLink>
                    ))}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;