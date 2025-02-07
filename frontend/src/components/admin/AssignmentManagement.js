import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi, assignmentApi } from '../../services/apiService';

const AssignmentManagement = () => {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddForm, setShowAddForm] = useState(false);
    const [formError, setFormError] = useState(null);
    const [formData, setFormData] = useState({
        week_id: '',
        title: '',
        description: '',
        type: 'homework',
        due_date: '',
        points_possible: 100,
        submission_type: 'text',
        late_submission_penalty: 10,
        is_published: false
    });
    const [assignments, setAssignments] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            setError(null);
            const response = await courseApi.getCourses();
            if (response.success) {
                setCourses(response.data.data.courses || []);
            } else {
                setError('Failed to load courses');
            }
        } catch (err) {
            setError('Failed to load courses');
            console.error('Error loading courses:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchAssignments = async () => {
        try {
            setError(null);
            const response = await assignmentApi.getAssignments(selectedCourse.id);
            console.log('Assignments response:', response); // Debug log
            if (response.success && response.data?.assignments) {
                setAssignments(response.data.assignments);
            } else {
                setError(response.message || 'Failed to load assignments: Invalid response format');
            }
        } catch (err) {
            console.error('Error loading assignments:', err);
            setError(err.message || 'Failed to load assignments');
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
        if (formError) setFormError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setFormError(null);
            const response = await courseApi.createAssignment(formData);
            if (response.success) {
                setShowAddForm(false);
                setFormData({
                    week_id: '',
                    title: '',
                    description: '',
                    type: 'homework',
                    due_date: '',
                    points_possible: 100,
                    submission_type: 'text',
                    late_submission_penalty: 10,
                    is_published: false
                });
                fetchCourses();
            } else {
                setFormError(response.error || 'Failed to create assignment');
            }
        } catch (err) {
            setFormError(err.message || 'Failed to create assignment');
            console.error('Error creating assignment:', err);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading courses...</div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Assignment Management</h1>
                <button
                    onClick={() => setShowAddForm(true)}
                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                >
                    Add New Assignment
                </button>
            </div>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            )}

            {/* Course Selection */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h2 className="text-xl font-semibold mb-4">Select Course</h2>
                <select
                    value={selectedCourse?.id || ''}
                    onChange={(e) => setSelectedCourse(courses.find(c => c.id === parseInt(e.target.value)))}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                    <option value="">Select a course...</option>
                    {courses.map(course => (
                        <option key={course.id} value={course.id}>
                            {course.code} - {course.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* Add Assignment Form */}
            {showAddForm && selectedCourse && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">Add New Assignment</h2>
                    {formError && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                            {formError}
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Week</label>
                            <select
                                name="week_id"
                                value={formData.week_id}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                required
                            >
                                <option value="">Select a week...</option>
                                {selectedCourse.weeks?.map(week => (
                                    <option key={week.id} value={week.id}>
                                        Week {week.number}: {week.title}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Title</label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Description</label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                rows="3"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Type</label>
                            <select
                                name="type"
                                value={formData.type}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                            >
                                <option value="homework">Homework</option>
                                <option value="practice">Practice</option>
                                <option value="graded">Graded</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Due Date</label>
                            <input
                                type="datetime-local"
                                name="due_date"
                                value={formData.due_date}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Points Possible</label>
                            <input
                                type="number"
                                name="points_possible"
                                value={formData.points_possible}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                min="0"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Submission Type</label>
                            <select
                                name="submission_type"
                                value={formData.submission_type}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                            >
                                <option value="text">Text</option>
                                <option value="file">File</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Late Submission Penalty (points per day)</label>
                            <input
                                type="number"
                                name="late_submission_penalty"
                                value={formData.late_submission_penalty}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                min="0"
                            />
                        </div>
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                name="is_published"
                                checked={formData.is_published}
                                onChange={handleInputChange}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label className="ml-2 block text-sm text-gray-900">
                                Publish immediately
                            </label>
                        </div>
                        <div className="flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={() => {
                                    setShowAddForm(false);
                                    setFormError(null);
                                }}
                                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                            >
                                Create Assignment
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Assignment List */}
            {selectedCourse && (
                <div className="space-y-6">
                    {selectedCourse.weeks?.map(week => (
                        <div key={week.id} className="bg-white rounded-lg shadow">
                            <div className="p-6 border-b border-gray-200">
                                <h2 className="text-xl font-semibold">Week {week.number}: {week.title}</h2>
                            </div>
                            <div className="p-6">
                                {week.assignments?.length > 0 ? (
                                    <div className="space-y-4">
                                        {week.assignments.map(assignment => (
                                            <div
                                                key={assignment.id}
                                                className="flex justify-between items-start p-4 bg-gray-50 rounded-lg"
                                            >
                                                <div>
                                                    <h3 className="font-medium">{assignment.title}</h3>
                                                    <p className="text-sm text-gray-600 mt-1">{assignment.description}</p>
                                                    <div className="mt-2 space-x-2">
                                                        <span className={`px-2 py-1 rounded text-xs ${
                                                            assignment.type === 'practice'
                                                                ? 'bg-blue-100 text-blue-800'
                                                                : assignment.type === 'graded'
                                                                ? 'bg-green-100 text-green-800'
                                                                : 'bg-yellow-100 text-yellow-800'
                                                        }`}>
                                                            {assignment.type.charAt(0).toUpperCase() + assignment.type.slice(1)}
                                                        </span>
                                                        <span className={`px-2 py-1 rounded text-xs ${
                                                            assignment.is_published
                                                                ? 'bg-green-100 text-green-800'
                                                                : 'bg-yellow-100 text-yellow-800'
                                                        }`}>
                                                            {assignment.is_published ? 'Published' : 'Draft'}
                                                        </span>
                                                    </div>
                                                </div>
                                                <div className="text-sm text-gray-600">
                                                    <p>Due: {new Date(assignment.due_date).toLocaleString()}</p>
                                                    <p>Points: {assignment.points_possible}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-gray-600 text-center">No assignments available for this week.</p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AssignmentManagement; 