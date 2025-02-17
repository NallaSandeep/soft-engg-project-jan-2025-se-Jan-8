import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

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
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading week data...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4">
                    {error}
                </div>
                <div className="mt-4 text-center">
                    <button
                        onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                        className="text-blue-600 hover:text-blue-800"
                    >
                        ← Back to Course Content
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <button
                        onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                        className="hover:text-blue-600"
                    >
                        Course Content
                    </button>
                    <span>→</span>
                    <span>Edit Week</span>
                </div>
                <h1 className="text-2xl font-bold text-gray-900">Edit Week</h1>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Week Number
                        </label>
                        <input
                            type="number"
                            value={weekData.number}
                            onChange={(e) => setWeekData(prev => ({ ...prev, number: parseInt(e.target.value) }))}
                            className="block w-full rounded-lg border border-gray-300 px-3 py-2"
                            required
                            min="1"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Title
                        </label>
                        <input
                            type="text"
                            value={weekData.title}
                            onChange={(e) => setWeekData(prev => ({ ...prev, title: e.target.value }))}
                            className="block w-full rounded-lg border border-gray-300 px-3 py-2"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Description
                        </label>
                        <textarea
                            value={weekData.description}
                            onChange={(e) => setWeekData(prev => ({ ...prev, description: e.target.value }))}
                            className="block w-full rounded-lg border border-gray-300 px-3 py-2"
                            rows="4"
                        />
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="is_published"
                            checked={weekData.is_published}
                            onChange={(e) => setWeekData(prev => ({ ...prev, is_published: e.target.checked }))}
                            className="h-4 w-4 text-blue-600 rounded border-gray-300"
                        />
                        <label htmlFor="is_published" className="ml-2 text-sm text-gray-700">
                            Published
                        </label>
                    </div>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                            className="px-4 py-2 text-gray-700 hover:text-gray-900"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
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