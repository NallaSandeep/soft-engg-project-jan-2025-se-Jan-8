import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const WeekEdit = ({ mode = 'edit' }) => {
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
    
    const isCreateMode = mode === 'create';

    useEffect(() => {
        if (isCreateMode) {
            fetchCourseData();
        } else {
            fetchWeekData();
        }
    }, [courseId, weekId, isCreateMode]);

    const fetchCourseData = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getCourseContent(courseId);
            
            if (response && response.success) {
                const weeks = response.data.weeks || [];
                const nextWeekNumber = weeks.length > 0 ? Math.max(...weeks.map(w => w.number || 0)) + 1 : 1;
                
                setWeekData({
                    number: nextWeekNumber,
                    title: '',
                    description: '',
                    is_published: false
                });
            } else {
                setError((response && response.message) || 'Failed to load course data.');
            }
        } catch (err) {
            console.error('Error loading course data:', err);
            setError('Failed to load course data. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    const fetchWeekData = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getCourseContent(courseId);
            
            if (response && response.success) {
                const week = response.data.weeks.find(w => w.id === parseInt(weekId));
                if (week) {
                    setWeekData({
                        number: week.number,
                        title: week.title,
                        description: week.description || '',
                        is_published: week.is_published
                    });
                } else {
                    setError('Week not found. Please go back to the course content page.');
                }
            } else {
                setError((response && response.message) || 'Failed to load week data. Please try again.');
            }
        } catch (err) {
            console.error('Error loading week data:', err);
            setError('Failed to load week data. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            
            let response;
            if (isCreateMode) {
                response = await courseApi.createWeek(courseId, {
                    ...weekData,
                    order: weekData.number
                });
            } else {
                response = await courseApi.updateWeek(courseId, weekId, weekData);
            }
            
            if (response && response.success) {
                navigate(`/ta/courses/${courseId}/content`);
            } else {
                const action = isCreateMode ? 'create' : 'update';
                setError((response && response.message) || `Failed to ${action} week. Please try again.`);
            }
        } catch (err) {
            console.error(`Error ${isCreateMode ? 'creating' : 'updating'} week:`, err);
            const action = isCreateMode ? 'create' : 'update';
            setError(`Failed to ${action} week. Please check your connection and try again.`);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">
                    {isCreateMode ? 'Preparing form...' : 'Loading week data...'}
                </span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg" role="alert">
                    <strong className="font-bold">Error!</strong>
                    <span className="block sm:inline"> {error}</span>
                </div>
                <div className="mt-4 text-center">
                    <button
                        onClick={() => navigate(`/ta/courses/${courseId}/content`)}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center justify-center gap-1"
                    >
                        <ArrowLeftIcon className="h-4 w-4" /> Back to Course Content
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <div className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                    <button
                        onClick={() => navigate(`/ta/courses/${courseId}/content`)}
                        className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"
                    >
                        <ArrowLeftIcon className="h-3 w-3" /> Course Content
                    </button>
                    <span>→</span>
                    <span>{isCreateMode ? "Add New Week" : "Edit Week"}</span>
                </div>
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                    {isCreateMode ? "Add New Week" : "Edit Week"}
                </h1>
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
                            className="mt-1 block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-2 bg-white dark:bg-zinc-800 shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 text-zinc-900 dark:text-white"
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
                            className="mt-1 block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-2 bg-white dark:bg-zinc-800 shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 text-zinc-900 dark:text-white"
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
                            className="mt-1 block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-2 bg-white dark:bg-zinc-800 shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 text-zinc-900 dark:text-white"
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
                            Published (visible to students)
                        </label>
                    </div>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={() => navigate(`/ta/courses/${courseId}/content`)}
                            className="bg-zinc-300 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 px-4 py-2 rounded hover:bg-zinc-400 dark:hover:bg-zinc-600 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white px-4 py-2 rounded shadow-sm hover:shadow-md transition-shadow"
                        >
                            {isCreateMode ? "Create Week" : "Save Changes"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default WeekEdit;