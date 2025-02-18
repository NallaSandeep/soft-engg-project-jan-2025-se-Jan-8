import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../common/Button';
import { personalApi } from '../../services/apiService';
import { showCreateKnowledgeBase } from './CreateKnowledgeBase';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';

const KnowledgeBaseLanding = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [knowledgeBases, setKnowledgeBases] = useState([]);

    useEffect(() => {
        loadKnowledgeBases();
    }, []);

    const loadKnowledgeBases = async () => {
        try {
            setLoading(true);
            const response = await personalApi.getKnowledgeBases();
            setKnowledgeBases(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to load knowledge bases');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateKB = () => {
        showCreateKnowledgeBase({
            onSuccess: loadKnowledgeBases
        });
    };

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorAlert message={error} />;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
                <h2 className="mt-2 text-3xl font-extrabold text-gray-900 sm:text-4xl">
                    Personal Knowledge Base
                </h2>
                <p className="mt-4 text-lg text-gray-500">
                    Organize your documents, notes, and resources in one place
                </p>
            </div>

            <div className="mt-12">
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {/* Create New KB Card */}
                    <div
                        className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 hover:bg-gray-50 cursor-pointer rounded-lg border border-gray-200"
                        onClick={handleCreateKB}
                    >
                        <div>
                            <Button variant="primary" className="w-full">
                                Create New Knowledge Base
                            </Button>
                        </div>
                        <p className="mt-2 text-sm text-gray-500">
                            Start organizing your knowledge with a new collection
                        </p>
                    </div>

                    {/* Existing Knowledge Bases */}
                    {knowledgeBases.map((kb) => (
                        <div
                            key={kb.id}
                            className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 hover:bg-gray-50 cursor-pointer rounded-lg border border-gray-200"
                            onClick={() => navigate(`/knowledge-base/${kb.id}`)}
                        >
                            <div className="mt-8">
                                <h3 className="text-lg font-medium">
                                    <span
                                        className="absolute inset-0"
                                        aria-hidden="true"
                                    />
                                    {kb.name}
                                </h3>
                                <p className="mt-2 text-sm text-gray-500">
                                    {kb.description || 'No description'}
                                </p>
                                <div className="mt-4 flex items-center text-sm text-gray-500">
                                    <span>{kb.document_count} documents</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default KnowledgeBaseLanding; 