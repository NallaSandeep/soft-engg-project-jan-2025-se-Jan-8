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
import 'bootstrap/dist/css/bootstrap.min.css';

const MenuItem = ({ to, icon: Icon, children }) => (
    <NavLink
        to={to}
        className={({ isActive }) =>
            `d-flex align-items-center gap-2 px-3 py-2 rounded transition ${
                isActive ? 'bg-warning text-dark fw-bold' : 'text-light hover-bg-secondary'
            }`
        }
    >
        <Icon size={20} />
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
        <div className="d-flex">
            {/* Sidebar */}
            <div
                className="bg-dark text-light shadow-lg p-3 d-flex flex-column"
                style={{
                    width: '250px',
                    height: '100vh',
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    backgroundColor: '#222',
                    overflowY: 'auto'
                }}
            >
                <h1 className="text-warning text-center fw-bold">StudyBot Admin</h1>
                <nav className="mt-4 flex-grow-1">
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
                </nav>

                <button
                    onClick={handleLogout}
                    className="d-flex align-items-center gap-2 w-100 mt-auto btn btn-outline-warning"
                >
                    <FaSignOutAlt size={20} />
                    <span>Logout</span>
                </button>
            </div>

            {/* Main Content */}
            <div
                className="flex-grow-1 text-white p-4"
                style={{
                    backgroundColor: '#000',
                    marginLeft: '250px',
                    height: '100vh',
                    overflowY: 'auto'
                }}
            >
                <Outlet />
            </div>
        </div>
    );
};

export default AdminLayout;
