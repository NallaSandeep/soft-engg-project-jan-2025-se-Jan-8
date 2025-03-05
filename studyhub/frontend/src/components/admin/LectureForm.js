import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const LectureForm = ({ mode = 'create' }) => {
    const navigate = useNavigate();
    const { courseId, weekId, lectureId } = useParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lectureData, setLectureData] = useState({
        title: '',
        description: '',
        youtube_url: '',
        is_published: false
    });

    useEffect(() => {
        if (mode === 'edit' && lectureId) {
            fetchLectureData();
        } else {
            setLoading(false);
        }
    }, [mode, lectureId]);

    const fetchLectureData = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getLectureContent(lectureId);
            if (response.success) {
                setLectureData({
                    title: response.data.title,
                    description: response.data.description || '',
                    youtube_url: response.data.youtube_url,
                    is_published: response.data.is_published
                });
            } else {
                setError(response.message || 'Failed to load lecture data');
            }
        } catch (err) {
            console.error('Error loading lecture data:', err);
            setError('Failed to load lecture data');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            let response;
            if (mode === 'edit') {
                response = await courseApi.updateLecture(lectureId, lectureData);
            } else {
                response = await courseApi.createLecture(courseId, weekId, lectureData);
            }

            if (response.success) {
                navigate(`/admin/courses/${courseId}/content`);
            } else {
                setError(response.message || `Failed to ${mode} lecture`);
            }
        } catch (err) {
            console.error(`Error ${mode}ing lecture:`, err);
            setError(`Failed to ${mode} lecture`);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4">
                    {error}
                </div>
                <div className="mt-4 text-center">
                    <button
                        onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center justify-center gap-1"
                    >
                        <ArrowLeftIcon className="h-4 w-4" /> Back to Course Content
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                    <button
                        onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                        className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"
                    >
                        <ArrowLeftIcon className="h-3 w-3" /> Course Content
                    </button>
                    <span>→</span>
                    <span>{mode === 'edit' ? 'Edit' : 'New'} Lecture</span>
                </div>
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                    {mode === 'edit' ? 'Edit' : 'Add New'} Lecture
                </h1>
            </div>

            <div className="glass-card p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Title
                        </label>
                        <input
                            type="text"
                            value={lectureData.title}
                            onChange={(e) => setLectureData(prev => ({ ...prev, title: e.target.value }))}
                            className="input-field"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Description
                        </label>
                        <textarea
                            value={lectureData.description}
                            onChange={(e) => setLectureData(prev => ({ ...prev, description: e.target.value }))}
                            className="input-field"
                            rows="4"
                        ></textarea>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            YouTube URL
                        </label>
                        <input
                            type="url"
                            value={lectureData.youtube_url}
                            onChange={(e) => setLectureData(prev => ({ ...prev, youtube_url: e.target.value }))}
                            className="input-field"
                            required
                            placeholder="https://www.youtube.com/watch?v=..."
                        />
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="is_published"
                            checked={lectureData.is_published}
                            onChange={(e) => setLectureData(prev => ({ ...prev, is_published: e.target.checked }))}
                            className="h-4 w-4 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400 rounded"
                        />
                        <label htmlFor="is_published" className="ml-2 text-sm text-zinc-700 dark:text-zinc-300">
                            Published
                        </label>
                    </div>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                            className="px-4 py-2 border border-zinc-300 dark:border-zinc-600 text-zinc-700 dark:text-zinc-300 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                        >
                            {mode === 'edit' ? 'Update' : 'Create'} Lecture
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default LectureForm; 