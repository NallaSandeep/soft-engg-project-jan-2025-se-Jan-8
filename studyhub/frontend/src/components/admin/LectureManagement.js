import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

const LectureManagement = () => {
    const { courseId, weekId } = useParams();
    const navigate = useNavigate();
    const [week, setWeek] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddForm, setShowAddForm] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        youtube_url: '',
        is_published: false
    });

    useEffect(() => {
        fetchWeekContent();
    }, [weekId]);

    const fetchWeekContent = async () => {
        try {
            setError(null);
            const response = await courseApi.getWeeks(courseId);
            if (response.success) {
                const foundWeek = response.data.find(w => w.id === parseInt(weekId));
                if (foundWeek) {
                    setWeek(foundWeek);
                } else {
                    setError('Week not found');
                }
            } else {
                setError(response.message || 'Failed to load week content');
            }
        } catch (err) {
            console.error('Error loading week content:', err);
            setError(err.message || 'Failed to load week content');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await courseApi.createLecture(weekId, formData);
            if (response.success) {
                setShowAddForm(false);
                setFormData({
                    title: '',
                    description: '',
                    youtube_url: '',
                    is_published: false
                });
                fetchWeekContent();
            } else {
                setError(response.message || 'Failed to create lecture');
            }
        } catch (err) {
            setError(err.message || 'Failed to create lecture');
        }
    };

    const handleDelete = async (lectureId) => {
        try {
            const response = await courseApi.deleteLecture(lectureId);
            if (response.success) {
                fetchWeekContent();
            } else {
                setError(response.message || 'Failed to delete lecture');
            }
        } catch (err) {
            setError(err.message || 'Failed to delete lecture');
        }
    };

    if (loading) return <div>Loading week content...</div>;
    if (error) return <div className="text-red-500">{error}</div>;
    if (!week) return <div>Week not found</div>;

    return (
        <div className="container mx-auto px-4 py-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold">Week {week.number}: {week.title}</h1>
                    <p className="text-gray-600">{week.description}</p>
                </div>
                <div className="space-x-2">
                    <button
                        onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                    >
                        Back to Course
                    </button>
                    <button
                        onClick={() => setShowAddForm(true)}
                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                    >
                        Add Lecture
                    </button>
                </div>
            </div>

            {/* Add Lecture Form */}
            {showAddForm && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">Add New Lecture</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Title</label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">YouTube URL</label>
                            <input
                                type="url"
                                name="youtube_url"
                                value={formData.youtube_url}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Description</label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                rows="3"
                            />
                        </div>
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                name="is_published"
                                checked={formData.is_published}
                                onChange={handleInputChange}
                                className="h-4 w-4 text-blue-600 rounded"
                            />
                            <label className="ml-2 text-sm text-gray-700">Publish Lecture</label>
                        </div>
                        <div className="flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={() => setShowAddForm(false)}
                                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                            >
                                Create Lecture
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Lectures List */}
            <div className="space-y-4">
                {week.lectures && week.lectures.length > 0 ? (
                    week.lectures.map(lecture => (
                        <div
                            key={lecture.id}
                            className="bg-white rounded-lg shadow p-4 flex justify-between items-center"
                        >
                            <div>
                                <h3 className="font-medium">{lecture.title}</h3>
                                <p className="text-sm text-gray-600">{lecture.description}</p>
                                <p className="text-sm text-gray-500">
                                    Status: {lecture.is_published ? 'Published' : 'Draft'}
                                </p>
                            </div>
                            <div className="space-x-2">
                                <button
                                    onClick={() => window.open(lecture.youtube_url, '_blank')}
                                    className="text-blue-500 hover:text-blue-600"
                                >
                                    View Video
                                </button>
                                <button
                                    onClick={() => handleDelete(lecture.id)}
                                    className="text-red-500 hover:text-red-600"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center py-8 bg-white rounded-lg shadow">
                        <p className="text-gray-600">No lectures added yet</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LectureManagement; 