import React, { useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { UploadIcon, XIcon } from '@heroicons/react/outline';
import kbService from '../../services/kbService';

const DocumentUpload = ({ isOpen, onClose, kbId, currentFolder, onSuccess }) => {
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selectedFiles = Array.from(e.target.files);
        setFiles(selectedFiles);
        setError(null);
    };

    const handleUpload = async () => {
        if (files.length === 0) {
            setError('Please select at least one file');
            return;
        }

        setUploading(true);
        setError(null);

        try {
            const uploadPromises = files.map(async (file) => {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('folder_path', currentFolder?.path || '/');

                // Upload to StudyIndexer first
                const indexerResponse = await fetch(`${process.env.REACT_APP_INDEXER_URL}/api/v1/documents/upload`, {
                    method: 'POST',
                    body: formData,
                });

                if (!indexerResponse.ok) {
                    throw new Error(`Failed to upload ${file.name}`);
                }

                const { document_id, metadata } = await indexerResponse.json();

                // Add to knowledge base
                await kbService.addDocument(
                    kbId,
                    document_id,
                    file.name,
                    file.type,
                    currentFolder?.id,
                    metadata
                );

                return document_id;
            });

            await Promise.all(uploadPromises);
            onSuccess();
            onClose();
        } catch (err) {
            setError(err.message || 'Failed to upload documents');
            console.error(err);
        } finally {
            setUploading(false);
        }
    };

    return (
        <Transition show={isOpen} as={React.Fragment}>
            <Dialog
                as="div"
                className="fixed inset-0 z-10 overflow-y-auto"
                onClose={onClose}
            >
                <div className="min-h-screen px-4 text-center">
                    <Transition.Child
                        as={React.Fragment}
                        enter="ease-out duration-300"
                        enterFrom="opacity-0"
                        enterTo="opacity-100"
                        leave="ease-in duration-200"
                        leaveFrom="opacity-100"
                        leaveTo="opacity-0"
                    >
                        <Dialog.Overlay className="fixed inset-0 bg-black opacity-30" />
                    </Transition.Child>

                    <span
                        className="inline-block h-screen align-middle"
                        aria-hidden="true"
                    >
                        &#8203;
                    </span>

                    <Transition.Child
                        as={React.Fragment}
                        enter="ease-out duration-300"
                        enterFrom="opacity-0 scale-95"
                        enterTo="opacity-100 scale-100"
                        leave="ease-in duration-200"
                        leaveFrom="opacity-100 scale-100"
                        leaveTo="opacity-0 scale-95"
                    >
                        <div className="inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl">
                            <Dialog.Title
                                as="h3"
                                className="text-lg font-medium leading-6 text-gray-900"
                            >
                                Upload Documents
                            </Dialog.Title>

                            <div className="mt-4">
                                <div
                                    className={`border-2 border-dashed rounded-lg p-6 text-center ${
                                        error ? 'border-red-300' : 'border-gray-300'
                                    }`}
                                >
                                    <input
                                        type="file"
                                        multiple
                                        onChange={handleFileChange}
                                        className="hidden"
                                        id="file-upload"
                                        accept=".pdf,.doc,.docx,.txt"
                                    />
                                    <label
                                        htmlFor="file-upload"
                                        className="cursor-pointer"
                                    >
                                        <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
                                        <span className="mt-2 block text-sm font-medium text-gray-900">
                                            {files.length > 0
                                                ? `${files.length} files selected`
                                                : 'Click to select files'}
                                        </span>
                                    </label>
                                </div>

                                {error && (
                                    <p className="mt-2 text-sm text-red-600">
                                        {error}
                                    </p>
                                )}

                                {files.length > 0 && (
                                    <div className="mt-4 space-y-2">
                                        {files.map((file, index) => (
                                            <div
                                                key={index}
                                                className="flex items-center justify-between text-sm"
                                            >
                                                <span className="truncate">
                                                    {file.name}
                                                </span>
                                                <button
                                                    onClick={() =>
                                                        setFiles(files.filter((_, i) => i !== index))
                                                    }
                                                    className="text-gray-400 hover:text-gray-500"
                                                >
                                                    <XIcon className="h-5 w-5" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="mt-6 flex justify-end space-x-3">
                                <button
                                    type="button"
                                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                    onClick={onClose}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="button"
                                    className={`px-4 py-2 text-sm font-medium text-white rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                                        uploading
                                            ? 'bg-blue-400 cursor-not-allowed'
                                            : 'bg-blue-600 hover:bg-blue-700'
                                    }`}
                                    onClick={handleUpload}
                                    disabled={uploading}
                                >
                                    {uploading ? 'Uploading...' : 'Upload'}
                                </button>
                            </div>
                        </div>
                    </Transition.Child>
                </div>
            </Dialog>
        </Transition>
    );
};

export default DocumentUpload; 