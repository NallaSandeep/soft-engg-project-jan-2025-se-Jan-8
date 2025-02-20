import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import ThemeToggle from '../themeToggle/ThemeToggle';

const Navbar = () => {
    const user = {
        role: 'student',
        first_name: 'John',
        last_name: 'Doe'
    };
    const navigate = useNavigate();
    
    const logout = () => {
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
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
        <nav className="sticky top-0 z-20 bg-zinc-100 dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16 items-center">
                    {/* Logo */}
                    <div className="flex items-center space-x-8">
                        <Link to={"/"+user.role+"/dashboard"} className="text-xl font-bold text-zinc-900 dark:text-white no-underline">
                            StudyHub
                        </Link>

                        {/* Desktop Navigation */}
                        <div className="hidden md:flex space-x-6">
                            {getNavLinks().map((link) => (
                                <NavLink
                                    key={link.to}
                                    to={link.to}
                                    className={({ isActive }) =>
                                        `px-1 py-2 text-sm font-medium transition-all duration-200 relative
                                        ${isActive 
                                            ? 'text-zinc-900 dark:text-white' 
                                            : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
                                        }
                                        after:absolute after:bottom-0 after:left-0 after:h-0.5 
                                        after:w-full after:bg-zinc-900 after:dark:bg-white 
                                        after:transform after:origin-bottom-left
                                        after:transition-transform after:duration-200
                                        ${isActive ? 'after:scale-x-100' : 'after:scale-x-0 hover:after:scale-x-100'} no-underline`
                                    }
                                >
                                    {link.text}
                                </NavLink>
                            ))}
                        </div>
                    </div>

                    {/* User Info & Actions */}
                    <div className="flex items-center space-x-6">
                        <span className="text-sm text-zinc-600 dark:text-zinc-400">
                            {user.role === 'student' ? 'Welcome, Student' : `Welcome, ${user.first_name} ${user.last_name}`}
                        </span>
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
                <div className="px-2 py-3">
                    {getNavLinks().map((link) => (
                        <NavLink
                            key={link.to}
                            to={link.to}
                            className={({ isActive }) =>
                                `block px-3 py-2 text-base font-medium transition-all duration-200
                                ${isActive 
                                    ? 'text-zinc-900 dark:text-white border-l-2 border-zinc-900 dark:border-white pl-4' 
                                    : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white'
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