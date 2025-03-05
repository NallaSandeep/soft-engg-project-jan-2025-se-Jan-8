import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const WeekEdit = () => {
    const navigate = useNavigate();
    const { courseId, weekId } = useParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [weekData, setWeekData] = useState({
        number: '',
        title: '',
        description: '',
        is_published: false
    });

    useEffect(() => {
        fetchWeekData();
    }, [courseId, weekId]);

    const fetchWeekData = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getCourseContent(courseId);
            if (response.success) {
                const week = response.data.weeks.find(w => w.id === parseInt(weekId));
                if (week) {
                    setWeekData({
                        number: week.number,
                        title: week.title,
                        description: week.description || '',
                        is_published: week.is_published
                    });
                } else {
                    setError('Week not found');
                }
            } else {
                setError(response.message || 'Failed to load week data');
            }
        } catch (err) {
            console.error('Error loading week data:', err);
            setError('Failed to load week data');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await courseApi.updateWeek(courseId, weekId, weekData);
            if (response.success) {
                navigate(`/admin/courses/${courseId}/content`);
            } else {
                setError(response.message || 'Failed to update week');
            }
        } catch (err) {
            console.error('Error updating week:', err);
            setError('Failed to update week');
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
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                    >
                        <span className="flex items-center justify-center gap-1">
                            <ArrowLeftIcon className="h-4 w-4" /> Back to Course Content
                        </span>
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
                    <span>Edit Week</span>
                </div>
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Edit Week</h1>
            </div>

            <div className="glass-card p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Week Number
                        </label>
                        <input
                            type="number"
                            value={weekData.number}
                            onChange={(e) => setWeekData(prev => ({ ...prev, number: parseInt(e.target.value) }))}
                            className="input-field"
                            required
                            min="1"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Title
                        </label>
                        <input
                            type="text"
                            value={weekData.title}
                            onChange={(e) => setWeekData(prev => ({ ...prev, title: e.target.value }))}
                            className="input-field"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Description
                        </label>
                        <textarea
                            value={weekData.description}
                            onChange={(e) => setWeekData(prev => ({ ...prev, description: e.target.value }))}
                            className="input-field"
                            rows="4"
                        ></textarea>
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="is_published"
                            checked={weekData.is_published}
                            onChange={(e) => setWeekData(prev => ({ ...prev, is_published: e.target.checked }))}
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
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default WeekEdit; 