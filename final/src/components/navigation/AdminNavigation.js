import React from 'react';
import { NavLink } from 'react-router-dom';

const AdminNavigation = () => {
    return (
        <nav 
            className="position-fixed d-flex flex-column p-3 text-white"
            style={{ 
                backgroundColor: '#121212', 
                height: '100vh', 
                width: '250px', 
                overflowY: 'auto', 
                borderRight: '2px solid #ffc107'
            }}
        >
            {/* Dashboard */}
            <NavLink
                to="/admin/dashboard"
                className={({ isActive }) =>
                    `d-flex align-items-center px-3 py-2 fw-bold text-decoration-none rounded ${isActive ? 'text-warning bg-dark' : 'text-light hover-bg'}`
                }
                style={{ transition: '0.3s' }}
            >
                <svg className="me-2" width="20" height="20" fill="currentColor">
                    <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
                Dashboard
            </NavLink>

            {/* Sections */}
            {[
                { title: 'Course Management', links: [
                    { to: '/admin/courses', text: 'Manage Courses' },
                    { to: '/admin/lectures', text: 'Manage Lectures' },
                    { to: '/admin/assignments', text: 'Manage Assignments' },
                    { to: '/admin/question-bank', text: 'Question Bank' }
                ]},
                { title: 'User Management', links: [
                    { to: '/admin/students', text: 'Manage Students' },
                    { to: '/admin/teaching-assistants', text: 'Teaching Assistants' }
                ]},
                { title: 'Analytics', links: [
                    { to: '/admin/reports', text: 'Reports' },
                    { to: '/admin/system-logs', text: 'System Logs' }
                ]}
            ].map((section, index) => (
                <div key={index} className="mt-3">
                    <h6 className="px-3 text-warning text-uppercase small">{section.title}</h6>
                    {section.links.map((link, idx) => (
                        <NavLink
                            key={idx}
                            to={link.to}
                            className={({ isActive }) =>
                                `d-flex align-items-center ps-4 py-2 fw-medium text-decoration-none rounded ${isActive ? 'text-warning bg-dark' : 'text-light hover-bg'}`
                            }
                            style={{ transition: '0.3s' }}
                        >
                            {link.text}
                        </NavLink>
                    ))}
                </div>
            ))}
        </nav>
    );
};

export default AdminNavigation;
