import React, { useState } from 'react';
import { FaStar, FaEllipsisV, FaFile, FaFileWord, FaFilePdf } from 'react-icons/fa';
import { Menu } from '@headlessui/react';
import { format } from 'date-fns';
import { Card } from '../common/Card';

const DocumentIcon = ({ type }) => {
    switch (type.toLowerCase()) {
        case 'pdf':
            return <FaFilePdf className="text-red-500" />;
        case 'docx':
        case 'doc':
            return <FaFileWord className="text-blue-500" />;
        default:
            return <FaFile className="text-zinc-500 dark:text-zinc-400" />;
    }
};

const DocumentList = ({
    documents,
    onToggleFavorite,
    onUpdateImportance,
    onDeleteDocument,
    onViewDocument
}) => {
    const [sortBy, setSortBy] = useState('lastViewed');
    const [sortOrder, setSortOrder] = useState('desc');

    const sortedDocuments = [...documents].sort((a, b) => {
        let comparison = 0;
        switch (sortBy) {
            case 'title':
                comparison = a.title.localeCompare(b.title);
                break;
            case 'lastViewed':
                comparison = new Date(a.lastViewed) - new Date(b.lastViewed);
                break;
            case 'importance':
                comparison = a.importance - b.importance;
                break;
            default:
                comparison = 0;
        }
        return sortOrder === 'asc' ? comparison : -comparison;
    });

    const handleSort = (field) => {
        if (sortBy === field) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(field);
            setSortOrder('desc');
        }
    };

    return (
        <Card className="rounded-lg shadow">
            {/* Header */}
            <div className="flex items-center p-4 border-b border-zinc-200 dark:border-zinc-700">
                <button
                    onClick={() => handleSort('title')}
                    className={`flex-1 text-left font-medium ${
                        sortBy === 'title' ? 'text-blue-600 dark:text-blue-400' : 'text-zinc-600 dark:text-zinc-400'
                    }`}
                >
                    Title
                    {sortBy === 'title' && (
                        <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                </button>
                <button
                    onClick={() => handleSort('lastViewed')}
                    className={`w-32 text-left font-medium ${
                        sortBy === 'lastViewed' ? 'text-blue-600 dark:text-blue-400' : 'text-zinc-600 dark:text-zinc-400'
                    }`}
                >
                    Last Viewed
                    {sortBy === 'lastViewed' && (
                        <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                </button>
                <button
                    onClick={() => handleSort('importance')}
                    className={`w-24 text-left font-medium ${
                        sortBy === 'importance' ? 'text-blue-600 dark:text-blue-400' : 'text-zinc-600 dark:text-zinc-400'
                    }`}
                >
                    Importance
                    {sortBy === 'importance' && (
                        <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                </button>
                <div className="w-8"></div>
            </div>

            {/* Document List */}
            <div className="divide-y divide-zinc-200 dark:divide-zinc-700">
                {sortedDocuments.map((doc) => (
                    <div
                        key={doc.id}
                        className="flex items-center p-4 hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors"
                    >
                        <div
                            className="flex-1 flex items-center cursor-pointer"
                            onClick={() => onViewDocument(doc)}
                        >
                            <DocumentIcon type={doc.type} />
                            <span className="ml-3 text-zinc-900 dark:text-white">{doc.title}</span>
                            {doc.tags.length > 0 && (
                                <div className="ml-4 flex gap-2">
                                    {doc.tags.map((tag) => (
                                        <span
                                            key={tag}
                                            className="px-2 py-1 text-xs rounded-full bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300"
                                        >
                                            #{tag}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                        <div className="w-32 text-sm text-zinc-500 dark:text-zinc-400">
                            {format(new Date(doc.lastViewed), 'MMM d, yyyy')}
                        </div>
                        <div className="w-24 flex items-center">
                            {[1, 2, 3, 4, 5].map((level) => (
                                <button
                                    key={level}
                                    onClick={() => onUpdateImportance(doc.id, level)}
                                    className={`w-4 h-4 rounded-full mx-0.5 ${
                                        level <= doc.importance
                                            ? 'bg-blue-600 dark:bg-blue-500'
                                            : 'bg-zinc-200 dark:bg-zinc-600'
                                    }`}
                                />
                            ))}
                        </div>
                        <div className="w-8 flex items-center">
                            <Menu as="div" className="relative">
                                <Menu.Button className="p-1 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-700">
                                    <FaEllipsisV className="text-zinc-400 dark:text-zinc-500" />
                                </Menu.Button>
                                <Menu.Items className="absolute right-0 mt-2 w-48 bg-white dark:bg-zinc-800 rounded-lg shadow-lg z-10 border border-zinc-200 dark:border-zinc-700">
                                    <Menu.Item>
                                        {({ active }) => (
                                            <button
                                                className={`${
                                                    active ? 'bg-zinc-100 dark:bg-zinc-700' : ''
                                                } flex items-center w-full px-4 py-2 text-left text-sm text-zinc-900 dark:text-white`}
                                                onClick={() => onToggleFavorite(doc.id)}
                                            >
                                                <FaStar
                                                    className={`mr-2 ${
                                                        doc.favorite
                                                            ? 'text-yellow-500 dark:text-yellow-400'
                                                            : 'text-zinc-400 dark:text-zinc-500'
                                                    }`}
                                                />
                                                {doc.favorite ? 'Remove from' : 'Add to'} Favorites
                                            </button>
                                        )}
                                    </Menu.Item>
                                    <Menu.Item>
                                        {({ active }) => (
                                            <button
                                                className={`${
                                                    active ? 'bg-zinc-100 dark:bg-zinc-700' : ''
                                                } flex items-center w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400`}
                                                onClick={() => onDeleteDocument(doc.id)}
                                            >
                                                Delete Document
                                            </button>
                                        )}
                                    </Menu.Item>
                                </Menu.Items>
                            </Menu>
                        </div>
                    </div>
                ))}

                {documents.length === 0 && (
                    <div className="p-8 text-center text-zinc-500 dark:text-zinc-400">
                        No documents found matching your criteria
                    </div>
                )}
            </div>
        </Card>
    );
};

export default DocumentList; 