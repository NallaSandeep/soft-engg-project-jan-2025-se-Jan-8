import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import FolderTree from './FolderTree';
import SearchBar from './SearchBar';
import DocumentList from './DocumentList';
import { kbService } from '../../services/kbService';
import { Card } from '../common/Card';

const PersonalKnowledgeBase = () => {
    const [selectedKB, setSelectedKB] = useState(null);
    const [folders, setFolders] = useState([]);
    const [documents, setDocuments] = useState([]);
    const [selectedFolder, setSelectedFolder] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [filters, setFilters] = useState({
        favorite: false,
        importance: null,
        tags: []
    });

    useEffect(() => {
        loadKnowledgeBases();
    }, []);

    useEffect(() => {
        if (selectedKB) {
            loadFolders();
            loadDocuments();
        }
    }, [selectedKB]);

    const loadKnowledgeBases = async () => {
        try {
            const kbs = await kbService.getKnowledgeBases();
            if (kbs.length > 0) {
                setSelectedKB(kbs[0]);
            }
        } catch (error) {
            toast.error('Failed to load knowledge bases');
        }
    };

    const loadFolders = async () => {
        try {
            const folderTree = await kbService.getFolderStructure(selectedKB.id);
            setFolders(folderTree);
        } catch (error) {
            toast.error('Failed to load folders');
        }
    };

    const loadDocuments = async () => {
        try {
            const docs = await kbService.getDocuments(selectedKB.id, selectedFolder?.id);
            setDocuments(docs);
        } catch (error) {
            toast.error('Failed to load documents');
        }
    };

    const handleCreateFolder = async (name, parentId) => {
        try {
            await kbService.createFolder(selectedKB.id, name, parentId);
            loadFolders();
            toast.success('Folder created successfully');
        } catch (error) {
            toast.error('Failed to create folder');
        }
    };

    const handleToggleFavorite = async (documentId) => {
        try {
            await kbService.toggleFavorite(selectedKB.id, documentId);
            loadDocuments();
        } catch (error) {
            toast.error('Failed to update favorite status');
        }
    };

    const handleUpdateImportance = async (documentId, importance) => {
        try {
            await kbService.updateImportance(selectedKB.id, documentId, importance);
            loadDocuments();
        } catch (error) {
            toast.error('Failed to update importance');
        }
    };

    const handleDeleteDocument = async (documentId) => {
        if (window.confirm('Are you sure you want to delete this document?')) {
            try {
                await kbService.deleteDocument(selectedKB.id, documentId);
                loadDocuments();
                toast.success('Document deleted successfully');
            } catch (error) {
                toast.error('Failed to delete document');
            }
        }
    };

    const handleViewDocument = (document) => {
        // Implement document viewing logic
        console.log('Viewing document:', document);
    };

    const filteredDocuments = documents.filter((doc) => {
        const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesFavorite = !filters.favorite || doc.favorite;
        const matchesImportance = !filters.importance || doc.importance === filters.importance;
        const matchesTags =
            filters.tags.length === 0 ||
            filters.tags.every((tag) => doc.tags.includes(tag));

        return matchesSearch && matchesFavorite && matchesImportance && matchesTags;
    });

    return (
        <div className="h-full flex">
            {/* Sidebar */}
            <Card className="w-64 border-r border-zinc-200 dark:border-zinc-700 p-4">
                <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">Folders</h2>
                <FolderTree
                    folders={folders}
                    selectedFolder={selectedFolder}
                    onSelectFolder={setSelectedFolder}
                    onCreateFolder={handleCreateFolder}
                />
            </Card>

            {/* Main Content */}
            <div className="flex-1 p-6 bg-zinc-50 dark:bg-zinc-800">
                <SearchBar
                    value={searchQuery}
                    onChange={setSearchQuery}
                    filters={filters}
                    onFilterChange={(newFilters) =>
                        setFilters({ ...filters, ...newFilters })
                    }
                />

                <div className="mt-6">
                    <DocumentList
                        documents={filteredDocuments}
                        onToggleFavorite={handleToggleFavorite}
                        onUpdateImportance={handleUpdateImportance}
                        onDeleteDocument={handleDeleteDocument}
                        onViewDocument={handleViewDocument}
                    />
                </div>
            </div>
        </div>
    );
};

export default PersonalKnowledgeBase; 