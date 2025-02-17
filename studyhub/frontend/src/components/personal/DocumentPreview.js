import React, { useState, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XIcon, StarIcon, TagIcon, LinkIcon, DocumentTextIcon } from '@heroicons/react/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/solid';
import kbService from '../../services/kbService';

const DocumentPreview = ({ isOpen, onClose, document, kbId, onUpdate }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [content, setContent] = useState(null);
    const [relatedDocs, setRelatedDocs] = useState([]);
    const [editMode, setEditMode] = useState(false);
    const [editData, setEditData] = useState({});

    useEffect(() => {
        if (isOpen && document) {
            loadDocumentContent();
            loadRelatedDocuments();
            setEditData({
                title: document.title,
                description: document.description || '',
                is_favorite: document.is_favorite,
                importance: document.importance,
                tags: document.tags || [],
                source_url: document.source_url || ''
            });
        }
    }, [isOpen, document]);

    const loadDocumentContent = async () => {
        try {
            setLoading(true);
            const response = await fetch(
                `${process.env.REACT_APP_INDEXER_URL}/api/v1/documents/${document.document_id}/content`,
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                }
            );
            const data = await response.json();
            setContent(data.content);
            setError(null);
        } catch (err) {
            setError('Failed to load document content');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const loadRelatedDocuments = async () => {
        try {
            const response = await kbService.getRelatedDocuments(document.document_id);
            setRelatedDocs(response.data.documents);
        } catch (err) {
            console.error('Failed to load related documents:', err);
        }
    };

    const handleSave = async () => {
        try {
            setLoading(true);
            await kbService.updateDocument(kbId, document.document_id, editData);
            onUpdate();
            setEditMode(false);
            setError(null);
        } catch (err) {
            setError('Failed to update document');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleTagAdd = (tag) => {
        if (tag && !editData.tags.includes(tag)) {
            setEditData({
                ...editData,
                tags: [...editData.tags, tag]
            });
        }
    };

    const handleTagRemove = (tag) => {
        setEditData({
            ...editData,
            tags: editData.tags.filter(t => t !== tag)
        });
    };

    return (
        <Transition show={isOpen} as={React.Fragment}>
            <Dialog
                as="div"
                className="fixed inset-0 z-20 overflow-hidden"
                onClose={onClose}
            >
                <div className="absolute inset-0 overflow-hidden">
                    <Dialog.Overlay className="absolute inset-0 bg-black opacity-30" />

                    <div className="fixed inset-y-0 right-0 pl-10 max-w-full flex">
                        <Transition.Child
                            as={React.Fragment}
                            enter="transform transition ease-in-out duration-300"
                            enterFrom="translate-x-full"
                            enterTo="translate-x-0"
                            leave="transform transition ease-in-out duration-300"
                            leaveFrom="translate-x-0"
                            leaveTo="translate-x-full"
                        >
                            <div className="w-screen max-w-2xl">
                                <div className="h-full flex flex-col bg-white shadow-xl">
                                    <div className="flex-1 h-0 overflow-y-auto">
                                        <div className="py-6 px-4 bg-blue-700 sm:px-6">
                                            <div className="flex items-center justify-between">
                                                <Dialog.Title className="text-lg font-medium text-white">
                                                    {editMode ? (
                                                        <input
                                                            type="text"
                                                            className="w-full px-2 py-1 text-gray-900 rounded"
                                                            value={editData.title}
                                                            onChange={(e) =>
                                                                setEditData({
                                                                    ...editData,
                                                                    title: e.target.value
                                                                })
                                                            }
                                                        />
                                                    ) : (
                                                        document?.title
                                                    )}
                                                </Dialog.Title>
                                                <div className="flex items-center ml-3 h-7">
                                                    <button
                                                        type="button"
                                                        className="text-white hover:text-gray-200"
                                                        onClick={onClose}
                                                    >
                                                        <XIcon className="h-6 w-6" />
                                                    </button>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex-1 flex flex-col justify-between">
                                            <div className="px-4 divide-y divide-gray-200 sm:px-6">
                                                <div className="space-y-6 pt-6 pb-5">
                                                    {/* Metadata */}
                                                    <div>
                                                        <div className="flex items-center space-x-2">
                                                            <button
                                                                onClick={() =>
                                                                    editMode &&
                                                                    setEditData({
                                                                        ...editData,
                                                                        is_favorite: !editData.is_favorite
                                                                    })
                                                                }
                                                                disabled={!editMode}
                                                                className={`${
                                                                    editMode ? 'cursor-pointer' : 'cursor-default'
                                                                }`}
                                                            >
                                                                {editData.is_favorite ? (
                                                                    <StarSolidIcon className="h-5 w-5 text-yellow-400" />
                                                                ) : (
                                                                    <StarIcon className="h-5 w-5 text-gray-400" />
                                                                )}
                                                            </button>
                                                            <span className="text-sm text-gray-500">
                                                                Importance:{' '}
                                                                {editMode ? (
                                                                    <select
                                                                        value={editData.importance}
                                                                        onChange={(e) =>
                                                                            setEditData({
                                                                                ...editData,
                                                                                importance: parseInt(e.target.value)
                                                                            })
                                                                        }
                                                                        className="ml-1 border-gray-300 rounded-md"
                                                                    >
                                                                        {[1, 2, 3, 4, 5].map((n) => (
                                                                            <option key={n} value={n}>
                                                                                {n}
                                                                            </option>
                                                                        ))}
                                                                    </select>
                                                                ) : (
                                                                    editData.importance
                                                                )}
                                                            </span>
                                                        </div>

                                                        {/* Description */}
                                                        <div className="mt-4">
                                                            <label className="block text-sm font-medium text-gray-900">
                                                                Description
                                                            </label>
                                                            {editMode ? (
                                                                <textarea
                                                                    rows={3}
                                                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm"
                                                                    value={editData.description}
                                                                    onChange={(e) =>
                                                                        setEditData({
                                                                            ...editData,
                                                                            description: e.target.value
                                                                        })
                                                                    }
                                                                />
                                                            ) : (
                                                                <p className="mt-1 text-sm text-gray-500">
                                                                    {document?.description || 'No description'}
                                                                </p>
                                                            )}
                                                        </div>

                                                        {/* Tags */}
                                                        <div className="mt-4">
                                                            <label className="block text-sm font-medium text-gray-900">
                                                                Tags
                                                            </label>
                                                            <div className="mt-2 flex flex-wrap gap-2">
                                                                {editData.tags.map((tag) => (
                                                                    <span
                                                                        key={tag}
                                                                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                                                                    >
                                                                        {tag}
                                                                        {editMode && (
                                                                            <button
                                                                                type="button"
                                                                                onClick={() => handleTagRemove(tag)}
                                                                                className="ml-1 text-blue-400 hover:text-blue-600"
                                                                            >
                                                                                <XIcon className="h-3 w-3" />
                                                                            </button>
                                                                        )}
                                                                    </span>
                                                                ))}
                                                                {editMode && (
                                                                    <input
                                                                        type="text"
                                                                        placeholder="Add tag..."
                                                                        className="border-gray-300 rounded-md text-sm"
                                                                        onKeyPress={(e) => {
                                                                            if (e.key === 'Enter') {
                                                                                handleTagAdd(e.target.value);
                                                                                e.target.value = '';
                                                                            }
                                                                        }}
                                                                    />
                                                                )}
                                                            </div>
                                                        </div>

                                                        {/* Source URL */}
                                                        <div className="mt-4">
                                                            <label className="block text-sm font-medium text-gray-900">
                                                                Source URL
                                                            </label>
                                                            {editMode ? (
                                                                <input
                                                                    type="url"
                                                                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm"
                                                                    value={editData.source_url}
                                                                    onChange={(e) =>
                                                                        setEditData({
                                                                            ...editData,
                                                                            source_url: e.target.value
                                                                        })
                                                                    }
                                                                />
                                                            ) : (
                                                                <a
                                                                    href={document?.source_url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="mt-1 text-sm text-blue-600 hover:text-blue-800"
                                                                >
                                                                    {document?.source_url}
                                                                </a>
                                                            )}
                                                        </div>
                                                    </div>

                                                    {/* Content */}
                                                    <div>
                                                        <h3 className="text-sm font-medium text-gray-900">
                                                            Content
                                                        </h3>
                                                        {loading ? (
                                                            <div className="mt-2 animate-pulse">
                                                                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                                                                <div className="space-y-3 mt-4">
                                                                    <div className="h-4 bg-gray-200 rounded"></div>
                                                                    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                                                                </div>
                                                            </div>
                                                        ) : error ? (
                                                            <div className="mt-2 text-sm text-red-600">
                                                                {error}
                                                            </div>
                                                        ) : (
                                                            <div className="mt-2 prose prose-sm max-w-none">
                                                                {content}
                                                            </div>
                                                        )}
                                                    </div>

                                                    {/* Related Documents */}
                                                    {relatedDocs.length > 0 && (
                                                        <div>
                                                            <h3 className="text-sm font-medium text-gray-900">
                                                                Related Documents
                                                            </h3>
                                                            <ul className="mt-2 divide-y divide-gray-200">
                                                                {relatedDocs.map((doc) => (
                                                                    <li
                                                                        key={doc.id}
                                                                        className="py-2"
                                                                    >
                                                                        <div className="flex items-center space-x-3">
                                                                            <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                                                                            <div className="flex-1 min-w-0">
                                                                                <p className="text-sm font-medium text-gray-900 truncate">
                                                                                    {doc.title}
                                                                                </p>
                                                                                <p className="text-sm text-gray-500 truncate">
                                                                                    {doc.description}
                                                                                </p>
                                                                            </div>
                                                                        </div>
                                                                    </li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Footer */}
                                    <div className="flex-shrink-0 px-4 py-4 flex justify-end space-x-3 bg-gray-50">
                                        {editMode ? (
                                            <>
                                                <button
                                                    type="button"
                                                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                                    onClick={() => setEditMode(false)}
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    type="button"
                                                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                                    onClick={handleSave}
                                                    disabled={loading}
                                                >
                                                    Save Changes
                                                </button>
                                            </>
                                        ) : (
                                            <button
                                                type="button"
                                                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                                onClick={() => setEditMode(true)}
                                            >
                                                Edit
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition>
    );
};

export default DocumentPreview; 