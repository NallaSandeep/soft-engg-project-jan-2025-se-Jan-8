import React, { useState } from 'react';
import Modal from '../common/Modal/Modal';
import { useModal } from '../common/Modal/ModalContext';
import { kbApi } from '../../services/kbService';

const CreateKnowledgeBase = ({ onSuccess }) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const { closeModal } = useModal();

    const handleSubmit = async () => {
        if (!name.trim()) {
            setError('Name is required');
            return;
        }

        try {
            setLoading(true);
            setError(null);
            await kbApi.createKnowledgeBase({ name, description });
            onSuccess?.();
            closeModal('create-kb');
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to create knowledge base');
            console.error(err);
            return false;
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-4">
            <div>
                <label
                    htmlFor="name"
                    className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                >
                    Name
                </label>
                <input
                    type="text"
                    id="name"
                    className="mt-1 block w-full border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />
            </div>

            <div>
                <label
                    htmlFor="description"
                    className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
                >
                    Description
                </label>
                <textarea
                    id="description"
                    rows={3}
                    className="mt-1 block w-full border border-zinc-300 dark:border-zinc-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
            </div>

            {error && (
                <p className="text-sm text-red-600 dark:text-red-400">
                    {error}
                </p>
            )}
        </div>
    );
};

export const showCreateKnowledgeBase = (modalProps) => {
    const { showModal } = useModal();
    
    return showModal({
        id: 'create-kb',
        title: 'Create Knowledge Base',
        children: <CreateKnowledgeBase {...modalProps} />,
        onConfirm: async () => {
            const form = document.getElementById('create-kb-form');
            if (form) {
                return form.requestSubmit();
            }
        },
        loading: modalProps.loading,
        confirmText: 'Create',
        size: 'md'
    });
};

export default CreateKnowledgeBase; 