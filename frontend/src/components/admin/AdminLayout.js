import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
    FaHome,
    FaBook,
    FaUsers,
    FaClipboardList,
    FaQuestionCircle,
    FaSignOutAlt
} from 'react-icons/fa';

const MenuItem = ({ to, icon: Icon, children }) => (
    <NavLink
        to={to}
        className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
            }`
        }
    >
        <Icon className="w-5 h-5" />
        <span>{children}</span>
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
        <div className="min-h-screen bg-gray-100">
            <div className="flex">
                {/* Sidebar */}
                <div className="w-64 bg-white shadow-lg min-h-screen">
                    <div className="p-4">
                        <h1 className="text-xl font-bold text-gray-800">StudyBot Admin</h1>
                    </div>
                    <nav className="mt-4 space-y-2 px-2">
                        <MenuItem to="/admin/dashboard" icon={FaHome}>
                            Dashboard
                        </MenuItem>
                        <MenuItem to="/admin/courses" icon={FaBook}>
                            Courses
                        </MenuItem>
                        <MenuItem to="/admin/assignments" icon={FaClipboardList}>
                            Assignments
                        </MenuItem>
                        <MenuItem to="/admin/question-bank" icon={FaQuestionCircle}>
                            Question Bank
                        </MenuItem>
                        <MenuItem to="/admin/users" icon={FaUsers}>
                            Users
                        </MenuItem>
                        <button
                            onClick={handleLogout}
                            className="flex items-center space-x-2 px-4 py-2 w-full text-left text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            <FaSignOutAlt className="w-5 h-5" />
                            <span>Logout</span>
                        </button>
                    </nav>
                </div>

                {/* Main Content */}
                <div className="flex-1">
                    <div className="p-4">
                        <Outlet />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminLayout; 