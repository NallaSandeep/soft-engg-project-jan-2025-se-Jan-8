import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../common/Button';
import { personalApi } from '../../services/apiService';
import { showCreateKnowledgeBase } from './CreateKnowledgeBase';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';
import { Card } from '../common/Card';

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
                <h2 className="mt-2 text-3xl font-extrabold text-zinc-900 dark:text-white sm:text-4xl">
                    Personal Knowledge Base
                </h2>
                <p className="mt-4 text-lg text-zinc-500 dark:text-zinc-400">
                    Organize your documents, notes, and resources in one place
                </p>
            </div>

            <div className="mt-12">
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {/* Create New KB Card */}
                    <Card
                        className="p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 hover:bg-zinc-50 dark:hover:bg-zinc-700 cursor-pointer border border-zinc-200 dark:border-zinc-700 transition-colors"
                        onClick={handleCreateKB}
                    >
                        <div>
                            <Button variant="primary" className="w-full">
                                Create New Knowledge Base
                            </Button>
                        </div>
                        <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
                            Start organizing your knowledge with a new collection
                        </p>
                    </Card>

                    {/* Existing Knowledge Bases */}
                    {knowledgeBases.map((kb) => (
                        <Card
                            key={kb.id}
                            className="p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 hover:bg-zinc-50 dark:hover:bg-zinc-700 cursor-pointer border border-zinc-200 dark:border-zinc-700 transition-colors"
                            onClick={() => navigate(`/knowledge-base/${kb.id}`)}
                        >
                            <div className="mt-8">
                                <h3 className="text-lg font-medium text-zinc-900 dark:text-white">
                                    <span
                                        className="absolute inset-0"
                                        aria-hidden="true"
                                    />
                                    {kb.name}
                                </h3>
                                <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
                                    {kb.description || 'No description'}
                                </p>
                                <div className="mt-4 flex items-center text-sm text-zinc-500 dark:text-zinc-400">
                                    <span>{kb.document_count} documents</span>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default KnowledgeBaseLanding; 