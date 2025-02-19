import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../contexts/ThemeContext';
import kbService from '../../services/kbService';
import { 
    AcademicCapIcon,
    PlusIcon,
    BookOpenIcon,
    XMarkIcon,
    Bars3Icon,
    HomeIcon,
    UserGroupIcon,
    BookmarkIcon,
    ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';
import CreateKnowledgeBase from '../personal/CreateKnowledgeBase';

const Sidebar = () => {
    const { user } = useAuth();
    const { isDark } = useTheme();
    const [knowledgeBases, setKnowledgeBases] = useState([]);
    const [showCreateKB, setShowCreateKB] = useState(false);
    const [isMobileOpen, setIsMobileOpen] = useState(false);

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
                        { to: '/admin/dashboard', text: 'Dashboard', icon: HomeIcon },
                        { to: '/admin/users', text: 'Users', icon: UserGroupIcon },
                        { to: '/admin/courses', text: 'Courses', icon: BookmarkIcon }
                    ];
                case 'ta':
                    return [
                        { to: '/ta/dashboard', text: 'Dashboard', icon: HomeIcon },
                        { to: '/ta/courses', text: 'My Courses', icon: BookmarkIcon },
                        { to: '/ta/grading', text: 'Grade Assignments', icon: ClipboardDocumentListIcon }
                    ];
                case 'student':
                    return [
                        { to: '/student/dashboard', text: 'Dashboard', icon: HomeIcon },
                        { to: '/student/courses', text: 'My Courses', icon: BookmarkIcon },
                        { to: '/student/assignments', text: 'Assignments', icon: ClipboardDocumentListIcon }
                    ];
                default:
                    return [];
            }
        })();

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
        setShowCreateKB(false);
    };

    return (
        <>
            {/* Mobile Menu Button */}
            <button
                onClick={() => setIsMobileOpen(true)}
                className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-white dark:bg-zinc-800"
            >
                <Bars3Icon className="h-6 w-6 text-zinc-900 dark:text-white" />
            </button>

            {/* Sidebar */}
            <aside className={`fixed inset-y-0 left-0 z-40 w-72 bg-white dark:bg-zinc-900
                            transform transition-transform duration-200 ease-in-out 
                            ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0
                            border-r border-zinc-200 dark:border-zinc-800`}>
                <div className="h-full flex flex-col">
                    {/* Logo Section */}
                    <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
                        <div className="flex items-center space-x-3">
                            <AcademicCapIcon className="h-8 w-8 text-zinc-900 dark:text-white" />
                            <span className="text-lg font-semibold text-zinc-900 dark:text-white">
                                StudyHub
                            </span>
                        </div>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 p-4 space-y-8 overflow-y-auto">
                        {/* Main Links */}
                        <div className="space-y-1">
                            {groupedLinks['Main']?.map((link) => (
                                <NavLink
                                    key={link.to}
                                    to={link.to}
                                    onClick={() => setIsMobileOpen(false)}
                                    className={({ isActive }) =>
                                        `flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 
                                        ${isActive 
                                            ? 'bg-zinc-900 text-white dark:bg-white dark:text-zinc-900'
                                            : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800'
                                        }`
                                    }
                                >
                                    {link.icon && (
                                        <link.icon className="h-5 w-5 mr-3" />
                                    )}
                                    {link.text}
                                </NavLink>
                            ))}
                        </div>

                        {/* Knowledge Base Section */}
                        {groupedLinks['Knowledge Bases'] && (
                            <div className="space-y-4">
                                <div className="flex items-center justify-between px-4">
                                    <h3 className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                        Knowledge Bases
                                    </h3>
                                    <button
                                        onClick={() => setShowCreateKB(true)}
                                        className="p-1 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md transition-colors"
                                    >
                                        <PlusIcon className="h-4 w-4 text-zinc-500 dark:text-zinc-400" />
                                    </button>
                                </div>
                                <div className="space-y-1">
                                    {groupedLinks['Knowledge Bases'].map((link) => (
                                        <NavLink
                                            key={link.to}
                                            to={link.to}
                                            onClick={() => setIsMobileOpen(false)}
                                            className={({ isActive }) =>
                                                `flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors
                                                ${isActive 
                                                    ? 'bg-zinc-900 text-white dark:bg-white dark:text-zinc-900'
                                                    : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800'
                                                }`
                                            }
                                        >
                                            {link.icon && (
                                                <link.icon className="h-5 w-5 mr-3" />
                                            )}
                                            <span className="truncate">{link.text}</span>
                                        </NavLink>
                                    ))}
                                </div>
                            </div>
                        )}
                    </nav>
                </div>
            </aside>

            {/* Mobile Backdrop */}
            {isMobileOpen && (
                <div 
                    className="fixed inset-0 bg-zinc-900/20 md:hidden z-30"
                    onClick={() => setIsMobileOpen(false)}
                >
                    <button
                        onClick={() => setIsMobileOpen(false)}
                        className="absolute top-4 left-[19rem] p-2 rounded-lg bg-white dark:bg-zinc-800"
                    >
                        <XMarkIcon className="h-5 w-5 text-zinc-900 dark:text-white" />
                    </button>
                </div>
            )}

            <CreateKnowledgeBase
                isOpen={showCreateKB}
                onClose={() => setShowCreateKB(false)}
                onSuccess={handleCreateKBSuccess}
            />
        </>
    );
};

export default Sidebar;