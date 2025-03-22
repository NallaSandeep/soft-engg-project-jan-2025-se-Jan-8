import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import ThemeToggle from '../themeToggle/ThemeToggle';
import {
    HomeIcon,
    BookOpenIcon,
    UserGroupIcon,
    ClipboardDocumentListIcon,
    QuestionMarkCircleIcon,
    ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

const MenuItem = ({ to, icon: Icon, children }) => (
    <NavLink
        to={to}
        className={({ isActive }) =>
            `nav-link ${isActive ? 'active' : ''}`
        }
    >
        <Icon className="w-5 h-5" />
        <span className='ml-2'>{children}</span>
    </NavLink>
);

const AdminLayout = () => {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900">
            <div className="flex">
                {/* Sidebar */}
                <div className="hidden md:block w-64 bg-white dark:bg-zinc-800 shadow-md min-h-screen border-r border-zinc-200 dark:border-zinc-700">
                <div className="fixed w-64 bg-white dark:bg-zinc-800 shadow-md min-h-screen border-r border-zinc-200 dark:border-zinc-700">
                    <div className="p-4 flex justify-between items-center border-b border-zinc-200 dark:border-zinc-700">
                        <h1 className="text-xl font-bold text-zinc-900 dark:text-white">StudyHub Admin</h1>
                        <ThemeToggle />
                    </div>
                    <nav className="mt-4 space-y-1 px-2">
                        <MenuItem to="/admin/dashboard" icon={HomeIcon}>
                            Dashboard
                        </MenuItem>
                        <MenuItem to="/admin/courses" icon={BookOpenIcon}>
                            Courses
                        </MenuItem>
                        <MenuItem to="/admin/assignments" icon={ClipboardDocumentListIcon}>
                            Assignments
                        </MenuItem>
                        <MenuItem to="/admin/question-bank" icon={QuestionMarkCircleIcon}>
                            Question Bank
                        </MenuItem>
                        <MenuItem to="/admin/users" icon={UserGroupIcon}>
                            Users
                        </MenuItem>
                        <MenuItem to="/admin/enroll" icon={UserGroupIcon}>
                            Enroll
                        </MenuItem>
                        <div className="pt-4 mt-4 border-t border-zinc-200 dark:border-zinc-700">
                            <button
                                onClick={handleLogout}
                                className="flex items-center space-x-2 px-4 py-2.5 w-full text-left text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-700 hover:text-zinc-900 dark:hover:text-white rounded-lg"
                            >
                                <ArrowRightOnRectangleIcon className="w-5 h-5" />
                                <span>Logout</span>
                            </button>
                        </div>
                    </nav>
                </div>
                </div>

                {/* Main Content */}
                <div className="flex-1 bg-zinc-50 dark:bg-zinc-900 overflow-auto">
                    <div className="p-6 max-w-7xl mx-auto">
                        <Outlet />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminLayout; 