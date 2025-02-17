import React, { useState } from 'react';
import { FaFolder, FaFolderOpen, FaPlus, FaEllipsisV } from 'react-icons/fa';
import { Menu } from '@headlessui/react';
import { toast } from 'react-toastify';

const FolderTree = ({ folders, selectedFolder, onSelect, onCreateFolder }) => {
    const [expandedFolders, setExpandedFolders] = useState(new Set());
    const [newFolderParentId, setNewFolderParentId] = useState(null);
    const [newFolderName, setNewFolderName] = useState('');

    const toggleFolder = (folderId) => {
        const newExpanded = new Set(expandedFolders);
        if (newExpanded.has(folderId)) {
            newExpanded.delete(folderId);
        } else {
            newExpanded.add(folderId);
        }
        setExpandedFolders(newExpanded);
    };

    const handleCreateFolder = (parentId = null) => {
        setNewFolderParentId(parentId);
        setNewFolderName('');
    };

    const submitNewFolder = async () => {
        if (!newFolderName.trim()) {
            toast.error('Please enter a folder name');
            return;
        }
        await onCreateFolder(newFolderName.trim(), newFolderParentId);
        setNewFolderName('');
        setNewFolderParentId(null);
    };

    const renderFolder = (folder) => {
        const isExpanded = expandedFolders.has(folder.id);
        const isSelected = selectedFolder?.id === folder.id;
        const isCreatingHere = newFolderParentId === folder.id;

        return (
            <div key={folder.id} className="mb-1">
                <div
                    className={`flex items-center p-2 rounded cursor-pointer hover:bg-gray-100 ${
                        isSelected ? 'bg-blue-50' : ''
                    }`}
                >
                    <div
                        className="flex items-center flex-1"
                        onClick={() => {
                            toggleFolder(folder.id);
                            onSelect(folder);
                        }}
                    >
                        {isExpanded ? (
                            <FaFolderOpen className="text-yellow-500 mr-2" />
                        ) : (
                            <FaFolder className="text-yellow-500 mr-2" />
                        )}
                        <span className="text-sm">{folder.name}</span>
                        {folder.document_count > 0 && (
                            <span className="ml-2 text-xs text-gray-500">
                                ({folder.document_count})
                            </span>
                        )}
                    </div>

                    <Menu as="div" className="relative">
                        <Menu.Button className="p-1 hover:bg-gray-200 rounded">
                            <FaEllipsisV className="text-gray-500 text-sm" />
                        </Menu.Button>
                        <Menu.Items className="absolute right-0 mt-1 w-48 bg-white rounded shadow-lg z-10">
                            <Menu.Item>
                                {({ active }) => (
                                    <button
                                        className={`${
                                            active ? 'bg-gray-100' : ''
                                        } w-full text-left px-4 py-2 text-sm`}
                                        onClick={() => handleCreateFolder(folder.id)}
                                    >
                                        Create Subfolder
                                    </button>
                                )}
                            </Menu.Item>
                        </Menu.Items>
                    </Menu>
                </div>

                {isCreatingHere && (
                    <div className="ml-8 mt-2 flex items-center">
                        <input
                            type="text"
                            value={newFolderName}
                            onChange={(e) => setNewFolderName(e.target.value)}
                            placeholder="New folder name"
                            className="text-sm border rounded px-2 py-1 mr-2"
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                    submitNewFolder();
                                }
                            }}
                            autoFocus
                        />
                        <button
                            onClick={submitNewFolder}
                            className="text-sm bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
                        >
                            Create
                        </button>
                        <button
                            onClick={() => setNewFolderParentId(null)}
                            className="text-sm text-gray-600 px-2 py-1 ml-1 hover:text-gray-800"
                        >
                            Cancel
                        </button>
                    </div>
                )}

                {isExpanded && folder.subfolders && folder.subfolders.length > 0 && (
                    <div className="ml-6 mt-1 border-l-2 border-gray-200 pl-2">
                        {folder.subfolders.map((subfolder) => renderFolder(subfolder))}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-600">Folders</h3>
                <button
                    onClick={() => handleCreateFolder()}
                    className="text-sm text-blue-600 hover:text-blue-800"
                >
                    <FaPlus />
                </button>
            </div>

            {newFolderParentId === null && (
                <div className="mb-4">
                    <input
                        type="text"
                        value={newFolderName}
                        onChange={(e) => setNewFolderName(e.target.value)}
                        placeholder="New folder name"
                        className="text-sm border rounded px-2 py-1 w-full mb-2"
                        onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                                submitNewFolder();
                            }
                        }}
                    />
                    <div className="flex justify-end">
                        <button
                            onClick={submitNewFolder}
                            className="text-sm bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
                        >
                            Create
                        </button>
                        <button
                            onClick={() => setNewFolderName('')}
                            className="text-sm text-gray-600 px-2 py-1 ml-1 hover:text-gray-800"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            <div className="overflow-y-auto max-h-[calc(100vh-200px)]">
                {folders.map((folder) => renderFolder(folder))}
            </div>
        </div>
    );
};

export default FolderTree; 