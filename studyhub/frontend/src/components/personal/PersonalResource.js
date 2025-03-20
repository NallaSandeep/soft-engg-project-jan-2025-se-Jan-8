import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { personalApi } from '../../services/apiService';
import { Button, IconButton } from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';
import { PencilIcon, TrashIcon, EyeIcon, DocumentTextIcon, DocumentIcon, PlusIcon } from '@heroicons/react/24/outline';

const FileItem = ({ file, resourceId, onDelete, onEdit }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [downloadError, setDownloadError] = useState(null);

    const getPreviewText = (text, maxLength = 150) => {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };

    const handleDownload = async () => {
        try {
            setDownloadError(null);
            await personalApi.downloadFile(resourceId, file.id);
        } catch (error) {
            setDownloadError('Failed to download file. Please try again.');
            console.error('Download error:', error);
        }
    };

    return (
        <div className="bg-white dark:bg-zinc-700 rounded-lg p-4 mb-3 border border-zinc-200 dark:border-zinc-600">
            <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                    {file.type === 'text' ? (
                        <DocumentTextIcon className="h-5 w-5 text-zinc-600 dark:text-gray-400 mt-1" />
                    ) : (
                        <DocumentIcon className="h-5 w-5 text-zinc-600 dark:text-gray-400 mt-1" />
                    )}
                    <div className="flex-1">
                        <h4 className="text-sm font-medium text-zinc-900 dark:text-white">{file.name}</h4>
                        <p className="text-xs text-zinc-600 dark:text-gray-400">
                            Added {new Date(file.created_at).toLocaleDateString()}
                        </p>
                        {downloadError && (
                            <p className="text-xs text-red-500 mt-1">{downloadError}</p>
                        )}
                        {file.type === 'text' && (
                            <div className="mt-2">
                                <p className="text-sm text-zinc-600 dark:text-gray-300 whitespace-pre-wrap">
                                    {isExpanded ? file.content : getPreviewText(file.content)}
                                </p>
                                {file.content?.length > 150 && (
                                    <button
                                        onClick={() => setIsExpanded(!isExpanded)}
                                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm mt-1"
                                    >
                                        {isExpanded ? 'Show less' : 'Show more'}
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                    {file.type === 'text' ? (
                        <IconButton
                            onClick={() => onEdit(file)}
                            icon={<PencilIcon className="h-4 w-4" />}
                            variant="secondary"
                            size="sm"
                            title="Edit"
                        />
                    ) : (
                        <IconButton
                            onClick={handleDownload}
                            icon={<EyeIcon className="h-4 w-4" />}
                            variant="secondary"
                            size="sm"
                            title="View"
                        />
                    )}
                    <IconButton
                        onClick={() => onDelete(file.id)}
                        icon={<TrashIcon className="h-4 w-4" />}
                        variant="secondary"
                        size="sm"
                        title="Delete"
                    />
                </div>
            </div>
        </div>
    );
};

const AddFileModal = ({ isOpen, onClose, onSubmit }) => {
    const [fileType, setFileType] = useState('file'); // 'file' or 'text'
    const [textContent, setTextContent] = useState('');
    const [textName, setTextName] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (fileType === 'text') {
            onSubmit({
                type: 'text',
                name: textName || 'Untitled Note.txt',
                content: textContent
            });
        } else if (selectedFile) {
            onSubmit({
                type: 'file',
                file: selectedFile
            });
        }
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-zinc-50 dark:bg-zinc-800 rounded-lg p-6 max-w-lg w-full border border-zinc-200 dark:border-zinc-700">
                <h2 className="text-xl font-bold text-zinc-900 dark:text-white mb-4">Add New Resource</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-zinc-900 dark:text-white mb-2">Type</label>
                        <div className="flex space-x-4">
                            <label className="inline-flex items-center text-zinc-900 dark:text-white">
                                <input
                                    type="radio"
                                    value="file"
                                    checked={fileType === 'file'}
                                    onChange={(e) => setFileType(e.target.value)}
                                    className="mr-2"
                                />
                                Upload File
                            </label>
                            <label className="inline-flex items-center text-zinc-900 dark:text-white">
                                <input
                                    type="radio"
                                    value="text"
                                    checked={fileType === 'text'}
                                    onChange={(e) => setFileType(e.target.value)}
                                    className="mr-2"
                                />
                                Create Text Note
                            </label>
                        </div>
                    </div>

                    {fileType === 'text' ? (
                        <>
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-zinc-900 dark:text-white mb-2">Note Name</label>
                                <input
                                    type="text"
                                    value={textName}
                                    onChange={(e) => setTextName(e.target.value)}
                                    placeholder="Enter note name"
                                    className="w-full p-2 border rounded bg-white dark:bg-zinc-700 border-zinc-300 dark:border-zinc-600 text-zinc-900 dark:text-white placeholder-zinc-500 dark:placeholder-zinc-400"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-zinc-900 dark:text-white mb-2">Content</label>
                                <textarea
                                    value={textContent}
                                    onChange={(e) => setTextContent(e.target.value)}
                                    placeholder="Enter your note content"
                                    rows={6}
                                    className="w-full p-2 border rounded bg-white dark:bg-zinc-700 border-zinc-300 dark:border-zinc-600 text-zinc-900 dark:text-white placeholder-zinc-500 dark:placeholder-zinc-400"
                                />
                            </div>
                        </>
                    ) : (
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-zinc-900 dark:text-white mb-2">File</label>
                            <input
                                type="file"
                                onChange={(e) => setSelectedFile(e.target.files[0])}
                                className="w-full text-zinc-900 dark:text-white"
                            />
                        </div>
                    )}

                    <div className="flex justify-end space-x-2">
                        <Button variant="secondary" onClick={onClose}>Cancel</Button>
                        <Button type="submit">Add Resource</Button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const EditFileModal = ({ isOpen, onClose, onSubmit, file }) => {
    const [textContent, setTextContent] = useState(file?.content || '');
    const [textName, setTextName] = useState(file?.name || '');

    useEffect(() => {
        if (file) {
            setTextContent(file.content || '');
            setTextName(file.name || '');
        }
    }, [file]);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({
            name: textName,
            content: textContent
        });
        onClose();
    };

    if (!isOpen || !file) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-zinc-50 dark:bg-zinc-800 rounded-lg p-6 max-w-lg w-full border border-zinc-200 dark:border-zinc-700">
                <h2 className="text-xl font-bold text-zinc-900 dark:text-white mb-4">Edit Text Note</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-zinc-900 dark:text-white mb-2">Note Name</label>
                        <input
                            type="text"
                            value={textName}
                            onChange={(e) => setTextName(e.target.value)}
                            placeholder="Enter note name"
                            className="w-full p-2 border rounded bg-white dark:bg-zinc-700 border-zinc-300 dark:border-zinc-600 text-zinc-900 dark:text-white placeholder-zinc-500 dark:placeholder-zinc-400"
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-zinc-900 dark:text-white mb-2">Content</label>
                        <textarea
                            value={textContent}
                            onChange={(e) => setTextContent(e.target.value)}
                            placeholder="Enter your note content"
                            rows={10}
                            className="w-full p-2 border rounded bg-white dark:bg-zinc-700 border-zinc-300 dark:border-zinc-600 text-zinc-900 dark:text-white placeholder-zinc-500 dark:placeholder-zinc-400"
                        />
                    </div>
                    <div className="flex justify-end space-x-2">
                        <Button variant="secondary" onClick={onClose}>Cancel</Button>
                        <Button type="submit">Save Changes</Button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const PersonalResource = () => {
    const { resourceId } = useParams();
    const navigate = useNavigate();
    const [resource, setResource] = useState(null);
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notFound, setNotFound] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [showEditFileModal, setShowEditFileModal] = useState(false);
    const [editingFile, setEditingFile] = useState(null);
    const [isEditMode, setIsEditMode] = useState(false);
    const [editedResource, setEditedResource] = useState(null);

    const loadResource = async () => {
        if (!resourceId) {
            setNotFound(true);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            setNotFound(false);

            console.log('Loading resource:', resourceId); // Debug log
            const resourceData = await personalApi.getResource(resourceId);
            console.log('Resource data:', resourceData); // Debug log
            
            if (!resourceData) {
                setNotFound(true);
                return;
            }
            setResource(resourceData);
            
            console.log('Loading files for resource:', resourceId); // Debug log
            const filesData = await personalApi.getResourceFiles(resourceId);
            console.log('Files data:', filesData); // Debug log
            setFiles(filesData || []);
        } catch (err) {
            console.error('Error loading resource:', err);
            if (err.response?.status === 404) {
                setNotFound(true);
            } else {
                setError('Failed to load resource');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        console.log('PersonalResource useEffect triggered with resourceId:', resourceId);
        loadResource();
    }, [resourceId]); // Only depend on resourceId, since loadResource is defined inside the component

    const handleAddFile = async (fileData) => {
        try {
            setLoading(true);
            if (fileData.type === 'text') {
                await personalApi.addFile(resourceId, fileData);
            } else {
                await personalApi.addFile(resourceId, fileData.file);
            }
            await loadResource();
        } catch (err) {
            setError('Failed to add file');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteResource = async () => {
        if (!window.confirm('Are you sure you want to delete this resource?')) {
            return;
        }

        try {
            setLoading(true);
            await personalApi.deleteResource(resourceId);
            navigate('/personal-resources');
        } catch (err) {
            setError('Failed to delete resource');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleEditResource = () => {
        setEditedResource({ ...resource });
        setIsEditMode(true);
    };

    const handleUpdateResource = async () => {
        try {
            setLoading(true);
            await personalApi.updateResource(resourceId, editedResource);
            setResource(editedResource);
            setIsEditMode(false);
        } catch (err) {
            setError('Failed to update resource');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleFileDelete = async (fileId) => {
        try {
            setLoading(true);
            await personalApi.deleteFile(resourceId, fileId);
            await loadResource();
        } catch (err) {
            setError('Failed to delete file');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleEditFile = (file) => {
        setEditingFile(file);
        setShowEditFileModal(true);
    };

    const handleUpdateFile = async (data) => {
        try {
            setLoading(true);
            await personalApi.updateFile(resourceId, editingFile.id, data);
            await loadResource(); // Reload to get updated data
            setEditingFile(null);
        } catch (err) {
            setError('Failed to update file');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <LoadingSpinner />
            </div>
        );
    }

    if (notFound) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-600 dark:text-gray-400 mb-4">Resource not found</p>
                <Button onClick={() => navigate('/personal-resources')}>Back to Resources</Button>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <ErrorAlert message={error} className="mb-4" />
                <Button onClick={() => navigate('/personal-resources')}>Back to Resources</Button>
            </div>
        );
    }

    if (!resource) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-600 dark:text-gray-400 mb-4">Unable to load resource</p>
                <Button onClick={() => navigate('/personal-resources')}>Back to Resources</Button>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => navigate('/personal-resources')}
                        className="text-zinc-600 dark:text-gray-400 hover:text-zinc-900 dark:hover:text-white"
                    >
                        ← Back
                    </button>
                    {isEditMode ? (
                        <div>
                            <input
                                type="text"
                                value={editedResource.name}
                                onChange={(e) => setEditedResource({ ...editedResource, name: e.target.value })}
                                className="text-2xl font-bold text-zinc-900 dark:text-white bg-transparent border-b border-zinc-300 dark:border-zinc-600 focus:outline-none focus:border-blue-500"
                            />
                            <textarea
                                value={editedResource.description}
                                onChange={(e) => setEditedResource({ ...editedResource, description: e.target.value })}
                                className="w-full mt-2 text-zinc-600 dark:text-gray-400 bg-transparent border-b border-zinc-300 dark:border-zinc-600 focus:outline-none focus:border-blue-500"
                                rows={2}
                            />
                        </div>
                    ) : (
                        <div>
                            <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">{resource?.name}</h1>
                            <p className="text-zinc-600 dark:text-gray-400 mt-1">{resource?.description}</p>
                        </div>
                    )}
                </div>
                <div className="flex items-center space-x-2">
                    {isEditMode ? (
                        <>
                            <Button variant="primary" onClick={handleUpdateResource}>Save</Button>
                            <Button variant="secondary" onClick={() => setIsEditMode(false)}>Cancel</Button>
                        </>
                    ) : (
                        <>
                            <Button variant="secondary" onClick={handleEditResource}>Edit</Button>
                            <Button variant="danger" onClick={handleDeleteResource}>Delete</Button>
                        </>
                    )}
                </div>
            </div>

            <div className="bg-zinc-50 dark:bg-zinc-800 rounded-lg p-6 border border-zinc-200 dark:border-zinc-700">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">Files</h2>
                    <Button onClick={() => setShowAddModal(true)}>+ Add Resource</Button>
                </div>

                {files.length > 0 ? (
                    <div className="space-y-3">
                        {files.map(file => (
                            <FileItem
                                key={file.id}
                                file={file}
                                resourceId={resourceId}
                                onDelete={handleFileDelete}
                                onEdit={handleEditFile}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <p className="text-zinc-600 dark:text-gray-400 mb-4">No files added yet</p>
                        <Button onClick={() => setShowAddModal(true)}>+ Add Your First Resource</Button>
                    </div>
                )}
            </div>

            {showAddModal && (
                <AddFileModal
                    isOpen={showAddModal}
                    onClose={() => setShowAddModal(false)}
                    onSubmit={handleAddFile}
                />
            )}

            {showEditFileModal && (
                <EditFileModal
                    isOpen={showEditFileModal}
                    onClose={() => setShowEditFileModal(false)}
                    onSubmit={handleUpdateFile}
                    file={editingFile}
                />
            )}
        </div>
    );
};

export default PersonalResource; 