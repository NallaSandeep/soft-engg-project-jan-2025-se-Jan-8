import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Button } from '../common/Button';
import { kbApi } from '../../services/kbService';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';
import { useModal } from '../common/Modal/ModalContext';
import { Card } from '../common/Card';

const KnowledgeBase = () => {
    const { kbId } = useParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [folders, setFolders] = useState([]);
    const [documents, setDocuments] = useState([]);
    const [currentFolder, setCurrentFolder] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const { showModal } = useModal();

    useEffect(() => {
        loadFolderStructure();
    }, [kbId]);

    useEffect(() => {
        if (currentFolder || searchQuery) {
            searchDocuments();
        }
    }, [currentFolder, searchQuery]);

    const loadFolderStructure = async () => {
        try {
            setLoading(true);
            const response = await kbApi.getFolderStructure(kbId);
            setFolders(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to load folder structure');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const searchDocuments = async () => {
        try {
            setLoading(true);
            const response = await kbApi.searchPersonalDocuments({
                text: searchQuery,
                filters: {
                    folder_path: currentFolder?.path
                }
            });
            setDocuments(response.data.documents);
            setError(null);
        } catch (err) {
            setError('Failed to load documents');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleFolderClick = (folder) => {
        setCurrentFolder(folder);
    };

    const handleSearch = (e) => {
        e.preventDefault();
        searchDocuments();
    };

    const handleUpload = () => {
        showModal({
            id: 'upload-document',
            title: 'Upload Document',
            children: (
                <div className="space-y-4">
                    <input
                        type="file"
                        className="block w-full text-sm text-zinc-500 dark:text-zinc-400
                            file:mr-4 file:py-2 file:px-4
                            file:rounded-full file:border-0
                            file:text-sm file:font-semibold
                            file:bg-blue-50 dark:file:bg-blue-900/30 file:text-blue-700 dark:file:text-blue-400
                            hover:file:bg-blue-100 dark:hover:file:bg-blue-800/40"
                        accept=".pdf,.doc,.docx,.txt"
                        multiple
                    />
                </div>
            ),
            onConfirm: async () => {
                // Handle file upload
                await searchDocuments();
            },
            confirmText: 'Upload',
            size: 'md'
        });
    };

    const handleDocumentClick = (doc) => {
        showModal({
            id: 'view-document',
            title: doc.title,
            children: (
                <div className="space-y-4">
                    <p className="text-sm text-zinc-500 dark:text-zinc-400">{doc.description}</p>
                    <div className="prose dark:prose-invert max-w-none">{doc.content}</div>
                </div>
            ),
            showFooter: false,
            size: 'lg'
        });
    };

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorAlert message={error} />;

    return (
        <div className="flex h-full">
            {/* Folder Navigation */}
            <div className="w-64 bg-zinc-50 dark:bg-zinc-800 border-r border-zinc-200 dark:border-zinc-700 p-4">
                <div className="mb-4">
                    <h2 className="text-lg font-semibold text-zinc-700 dark:text-zinc-300">Folders</h2>
                    <button
                        className="mt-2 flex items-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                        onClick={() => setCurrentFolder(null)}
                    >
                        All Documents
                    </button>
                </div>
                <div className="space-y-2">
                    {folders.map((folder) => (
                        <button
                            key={folder.id}
                            className={`flex items-center w-full p-2 rounded-md text-sm ${
                                currentFolder?.id === folder.id
                                    ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                                    : 'text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-700'
                            } transition-colors`}
                            onClick={() => handleFolderClick(folder)}
                        >
                            {folder.name}
                            <span className="ml-auto text-xs text-zinc-500 dark:text-zinc-400">
                                {folder.document_count}
                            </span>
                        </button>
                    ))}
                </div>
            </div>

            {/* Document List */}
            <div className="flex-1 p-4">
                <div className="mb-4 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                        {currentFolder ? currentFolder.name : 'All Documents'}
                    </h1>
                    <div className="flex items-center space-x-4">
                        <form onSubmit={handleSearch} className="flex items-center">
                            <input
                                type="text"
                                placeholder="Search documents..."
                                className="rounded-md border border-zinc-300 dark:border-zinc-600 px-4 py-2 w-64 bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                            <Button
                                type="submit"
                                variant="secondary"
                                className="ml-2"
                            >
                                Search
                            </Button>
                        </form>
                        <Button
                            variant="primary"
                            onClick={handleUpload}
                        >
                            Add Document
                        </Button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {documents.map((doc) => (
                        <Card
                            key={doc.id}
                            className="p-4 border border-zinc-200 dark:border-zinc-700 hover:shadow-md transition-shadow cursor-pointer"
                            onClick={() => handleDocumentClick(doc)}
                        >
                            <div className="flex items-start">
                                <div className="ml-3">
                                    <h3 className="text-sm font-medium text-zinc-900 dark:text-white">
                                        {doc.title}
                                    </h3>
                                    <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                                        {doc.description || 'No description'}
                                    </p>
                                    <div className="mt-2 flex items-center text-xs text-zinc-500 dark:text-zinc-400">
                                        <span>Last viewed: {doc.last_viewed || 'Never'}</span>
                                        <span className="mx-2">•</span>
                                        <span>Views: {doc.view_count}</span>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default KnowledgeBase; 