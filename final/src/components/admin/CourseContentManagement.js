import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

const CourseContentManagement = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeWeek, setActiveWeek] = useState(null);
    const [showAddWeekForm, setShowAddWeekForm] = useState(false);
    const [weekFormData, setWeekFormData] = useState({
        title: '',
        description: ''
    });

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await courseApi.getCourseContent(courseId);
            if (response.success) {
                setCourse(response.data);
            } else {
                setError(response.message || 'Failed to load course content');
            }
        } catch (err) {
            console.error('Error loading course content:', err);
            setError(err.message || 'Failed to load course content');
        } finally {
            setLoading(false);
        }
    };

    const handleAddWeek = async (e) => {
        e.preventDefault();
        try {
            await courseApi.createWeek(courseId, {
                ...weekFormData,
                order: (course.weeks?.length || 0) + 1
            });
            setShowAddWeekForm(false);
            setWeekFormData({ title: '', description: '' });
            fetchCourseContent();
        } catch (err) {
            console.error('Error adding week:', err);
            setError('Failed to add week');
        }
    };

    const handleDeleteWeek = async (weekId) => {
        if (!window.confirm('Are you sure you want to delete this week?')) return;
        try {
            await courseApi.deleteWeek(courseId, weekId);
            fetchCourseContent();
        } catch (err) {
            console.error('Error deleting week:', err);
            setError('Failed to delete week');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading course content...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-600 text-center">
                    {error}
                </div>
                <div className="mt-4 text-center">
                    <button
                        onClick={() => navigate('/admin/courses')}
                        className="text-blue-600 hover:text-blue-800"
                    >
                        ← Back to Courses
                    </button>
                </div>
            </div>
        );
    }

    if (!course) {
        return (
            <div className="p-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-600 text-center">
                    Course not found
                </div>
                <div className="mt-4 text-center">
                    <button
                        onClick={() => navigate('/admin/courses')}
                        className="text-blue-600 hover:text-blue-800"
                    >
                        ← Back to Courses
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
                        onClick={() => navigate('/admin/courses')}
                        className="hover:text-blue-600"
                    >
                        Courses
                    </button>
                    <span>→</span>
                    <span>{course.name}</span>
                </div>
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900">Course Content</h1>
                    <button
                        onClick={() => setShowAddWeekForm(true)}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                        Add Week
                    </button>
                </div>
            </div>

            {/* Add Week Form */}
            {showAddWeekForm && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-lg font-semibold mb-4">Add New Week</h2>
                    <form onSubmit={handleAddWeek} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Title</label>
                            <input
                                type="text"
                                value={weekFormData.title}
                                onChange={(e) => setWeekFormData(prev => ({ ...prev, title: e.target.value }))}
                                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Description</label>
                            <textarea
                                value={weekFormData.description}
                                onChange={(e) => setWeekFormData(prev => ({ ...prev, description: e.target.value }))}
                                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2"
                                rows="3"
                            />
                        </div>
                        <div className="flex justify-end gap-2">
                            <button
                                type="button"
                                onClick={() => setShowAddWeekForm(false)}
                                className="px-4 py-2 text-gray-700 hover:text-gray-900"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                            >
                                Add Week
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Weeks List */}
            <div className="space-y-6">
                {course.weeks?.length > 0 ? (
                    course.weeks.map((week, index) => (
                        <div
                            key={week.id}
                            className="bg-white rounded-lg shadow"
                        >
                            <div className="p-6 border-b border-gray-200">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h2 className="text-lg font-semibold">
                                            Week {index + 1}: {week.title}
                                        </h2>
                                        <p className="text-gray-600 mt-1">{week.description}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => setActiveWeek(activeWeek === week.id ? null : week.id)}
                                            className="text-gray-600 hover:text-gray-900"
                                        >
                                            {activeWeek === week.id ? 'Hide Content' : 'Show Content'}
                                        </button>
                                        <button
                                            onClick={() => handleDeleteWeek(week.id)}
                                            className="text-red-600 hover:text-red-800"
                                        >
                                            Delete Week
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {activeWeek === week.id && (
                                <div className="p-6 bg-gray-50">
                                    <div className="space-y-4">
                                        {/* Lectures */}
                                        <div>
                                            <div className="flex justify-between items-center mb-2">
                                                <h3 className="font-medium">Lectures</h3>
                                                <button
                                                    onClick={() => navigate(`/admin/courses/${courseId}/weeks/${week.id}/lectures/new`)}
                                                    className="text-blue-600 hover:text-blue-800"
                                                >
                                                    Add Lecture
                                                </button>
                                            </div>
                                            {week.lectures?.length > 0 ? (
                                                <div className="space-y-2">
                                                    {week.lectures.map(lecture => (
                                                        <div
                                                            key={lecture.id}
                                                            className="flex justify-between items-center p-3 bg-white rounded-lg"
                                                        >
                                                            <span>{lecture.title}</span>
                                                            <button
                                                                onClick={() => navigate(`/admin/courses/${courseId}/lectures/${lecture.id}`)}
                                                                className="text-blue-600 hover:text-blue-800"
                                                            >
                                                                Edit
                                                            </button>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="text-gray-500">No lectures added yet</p>
                                            )}
                                        </div>

                                        {/* Assignments */}
                                        <div>
                                            <div className="flex justify-between items-center mb-2">
                                                <h3 className="font-medium">Assignments</h3>
                                                <button
                                                    onClick={() => navigate(`/admin/courses/${courseId}/weeks/${week.id}/assignments/new`)}
                                                    className="text-blue-600 hover:text-blue-800"
                                                >
                                                    Add Assignment
                                                </button>
                                            </div>
                                            {week.assignments?.length > 0 ? (
                                                <div className="space-y-2">
                                                    {week.assignments.map(assignment => (
                                                        <div
                                                            key={assignment.id}
                                                            className="flex justify-between items-center p-3 bg-white rounded-lg"
                                                        >
                                                            <span>{assignment.title}</span>
                                                            <button
                                                                onClick={() => navigate(`/admin/courses/${courseId}/assignments/${assignment.id}`)}
                                                                className="text-blue-600 hover:text-blue-800"
                                                            >
                                                                Edit
                                                            </button>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="text-gray-500">No assignments added yet</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <div className="bg-white rounded-lg shadow p-8 text-center">
                        <p className="text-gray-600">No weeks added to this course yet.</p>
                        <p className="text-sm text-gray-500 mt-2">
                            Add weeks to organize your course content.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseContentManagement; 