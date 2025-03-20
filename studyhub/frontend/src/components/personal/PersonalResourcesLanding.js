import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../common/Button';
import { personalApi } from '../../services/apiService';
import { showCreateResource } from './CreateResource';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';

const ResourceCard = ({ resource, onClick }) => (
    <div 
        onClick={onClick}
        className="bg-zinc-50 dark:bg-zinc-800 rounded-lg p-6 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors border border-zinc-200 dark:border-zinc-700"
    >
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">{resource.name}</h3>
        <p className="text-zinc-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">{resource.description}</p>
        <div className="flex justify-between items-center text-sm">
            <div className="flex items-center text-zinc-600 dark:text-gray-400">
                <span>{resource.files?.length || 0} files</span>
            </div>
            <div className="text-zinc-600 dark:text-gray-400">
                Created {new Date(resource.created_at).toLocaleDateString()}
            </div>
        </div>
    </div>
);

const PersonalResourcesLanding = () => {
    const [resources, setResources] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        loadResources();
    }, []);

    const loadResources = async () => {
        try {
            setLoading(true);
            const response = await personalApi.getPersonalResources();
            setResources(response?.data || []);
            setError(null);
        } catch (err) {
            setError('Failed to load resources');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateResource = async () => {
        const success = await showCreateResource();
        if (success) {
            loadResources();
        }
    };

    const handleResourceClick = (resourceId) => {
        navigate(`/personal-resources/${resourceId}`);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <LoadingSpinner />
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Personal Resources</h1>
                    <p className="text-zinc-600 dark:text-gray-400 mt-1">Manage your course resources and study materials</p>
                </div>
                <Button onClick={handleCreateResource}>Create New Resource</Button>
            </div>

            {error && <ErrorAlert message={error} className="mb-6" />}

            {resources.length === 0 && !loading ? (
                <div className="text-center py-12">
                    <p className="text-gray-600 dark:text-gray-400 mb-4">No resources yet</p>
                    <Button onClick={handleCreateResource}>Create Your First Resource</Button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {resources.map(resource => (
                        <ResourceCard
                            key={resource.id}
                            resource={resource}
                            onClick={() => handleResourceClick(resource.id)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default PersonalResourcesLanding;