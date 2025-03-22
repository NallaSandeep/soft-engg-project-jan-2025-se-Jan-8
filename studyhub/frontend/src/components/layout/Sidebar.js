import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import kbService from '../../services/kbService';
import { PlusIcon, BookOpenIcon } from '@heroicons/react/outline';
import CreateKnowledgeBase from '../personal/CreateKnowledgeBase';

const Sidebar = () => {
    const { user } = useAuth();
    const [knowledgeBases, setKnowledgeBases] = useState([]);
    const [showCreateKB, setShowCreateKB] = useState(false);

    useEffect(() => {
        if (user) {
            loadKnowledgeBases();
        }
    }, [user]);

    const loadKnowledgeBases = async () => {
        try {
            const response = await kbService.getKnowledgeBases();
            setKnowledgeBases(response.data);
        } catch (err) {
            console.error('Failed to load knowledge bases:', err);
        }
    };

    const getNavLinks = () => {
        const roleLinks = (() => {
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
        })();

        // Add Knowledge Base links
        const kbLinks = [
            {
                to: '/knowledge-base',
                text: 'Knowledge Base',
                icon: BookOpenIcon,
                group: 'Knowledge Bases'
            },
            ...knowledgeBases.map(kb => ({
                to: `/knowledge-base/${kb.id}`,
                text: kb.name,
                group: 'Knowledge Bases'
            }))
        ];

        return [...roleLinks, ...kbLinks];
    };

    const groupedLinks = getNavLinks().reduce((acc, link) => {
        const group = link.group || 'Main';
        if (!acc[group]) {
            acc[group] = [];
        }
        acc[group].push(link);
        return acc;
    }, {});

    const handleCreateKBSuccess = () => {
        loadKnowledgeBases();
    };

    return (
        <aside className="w-64 bg-white shadow-lg fixed top-0 left-0 w-64 h-screen">
            <div className="p-4">
                <nav className="space-y-6">
                    {Object.entries(groupedLinks).map(([group, links]) => (
                        <div key={group}>
                            {group !== 'Main' && (
                                <div className="flex items-center justify-between px-4 mb-2">
                                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                        {group}
                                    </h3>
                                    <button
                                        onClick={() => setShowCreateKB(true)}
                                        className="text-gray-400 hover:text-gray-500"
                                        title="Create Knowledge Base"
                                    >
                                        <PlusIcon className="h-4 w-4" />
                                    </button>
                                </div>
                            )}
                            <div className="mt-2 space-y-1">
                                {links.map((link) => (
                                    <NavLink
                                        key={link.to}
                                        to={link.to}
                                        className={({ isActive }) =>
                                            `flex items-center px-4 py-2 rounded-lg transition-colors ${
                                                isActive
                                                    ? 'bg-blue-50 text-blue-700'
                                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                            }`
                                        }
                                    >
                                        {link.icon && (
                                            <link.icon className="h-5 w-5 mr-2" />
                                        )}
                                        {link.text}
                                    </NavLink>
                                ))}
                            </div>
                        </div>
                    ))}
                </nav>
            </div>

            <CreateKnowledgeBase
                isOpen={showCreateKB}
                onClose={() => setShowCreateKB(false)}
                onSuccess={handleCreateKBSuccess}
            />
        </aside>
    );
};

export default Sidebar; 