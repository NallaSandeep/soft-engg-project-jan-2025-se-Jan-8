import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

const CourseManagement = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddForm, setShowAddForm] = useState(false);
    const [formError, setFormError] = useState(null);
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        description: '',
        max_students: '',
        enrollment_type: 'open'
    });
    const navigate = useNavigate();

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            setError(null);
            const response = await courseApi.getCourses();
            console.log('Fetch courses response:', response); // Debug log
            if (response.data) {
                setCourses(response.data || []);
            } else {
                setError('Failed to load courses: Invalid response format');
            }
        } catch (err) {
            console.error('Error loading courses:', err);
            setError(err.message || 'Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (formError) setFormError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setFormError(null);
            const response = await courseApi.createCourse(formData);
            console.log('Create course response:', response); // Debug log
            if (response.msg === 'Course created successfully') {
                setShowAddForm(false);
                setFormData({
                    code: '',
                    name: '',
                    description: '',
                    max_students: '',
                    enrollment_type: 'open'
                });
                fetchCourses();
            } else {
                setFormError(response.message || response.error || 'Failed to create course');
            }
        } catch (err) {
            console.error('Error creating course:', err);
            setFormError(err.message || 'Failed to create course');
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
                <h1 className="text-2xl font-bold">Course Management</h1>
                <button
                    onClick={() => setShowAddForm(true)}
                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                >
                    Add New Course
                </button>
            </div>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            )}

            {/* Add Course Form */}
            {showAddForm && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">Add New Course</h2>
                    {formError && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                            {formError}
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Course Code</label>
                            <input
                                type="text"
                                name="code"
                                value={formData.code}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Course Name</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
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
                            <label className="block text-sm font-medium text-gray-700">Max Students</label>
                            <input
                                type="number"
                                name="max_students"
                                value={formData.max_students}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                min="1"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Enrollment Type</label>
                            <select
                                name="enrollment_type"
                                value={formData.enrollment_type}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                            >
                                <option value="open">Open</option>
                                <option value="closed">Closed</option>
                                <option value="invite_only">Invite Only</option>
                            </select>
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
                                Create Course
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Course List */}
            <div className="grid grid-cols-1 gap-6">
                {courses.length > 0 ? (
                    courses.map(course => (
                        <div key={course.id} className="bg-white rounded-lg shadow p-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h2 className="text-xl font-semibold mb-2">{course.name}</h2>
                                    <p className="text-gray-600 mb-2">{course.code}</p>
                                    <p className="text-gray-700 mb-4">{course.description}</p>
                                    <div className="text-sm text-gray-600">
                                        <p>Max Students: {course.max_students || 'Unlimited'}</p>
                                        <p>Enrollment: {course.enrollment_type}</p>
                                    </div>
                                </div>
                                <div className="space-x-2">
                                    <button
                                        onClick={() => navigate(`/admin/courses/${course.id}/content`)}
                                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                    >
                                        Manage Content
                                    </button>
                                    <button
                                        onClick={() => navigate(`/admin/courses/${course.id}/edit`)}
                                        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                                    >
                                        Edit Course
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center py-8 bg-white rounded-lg shadow">
                        <p className="text-gray-600">No courses available. Create your first course!</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseManagement; 