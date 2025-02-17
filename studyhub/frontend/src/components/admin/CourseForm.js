import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { toast } from 'react-hot-toast';

const CourseForm = () => {
    const navigate = useNavigate();
    const { courseId } = useParams();
    const isEditMode = Boolean(courseId);

    const [loading, setLoading] = useState(isEditMode);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        description: '',
        max_students: 30,
        enrollment_type: 'open',
        start_date: '',
        end_date: '',
        is_active: true
    });

    useEffect(() => {
        if (isEditMode) {
            fetchCourse();
        }
    }, [courseId]);

    const fetchCourse = async () => {
        try {
            const response = await courseApi.getCourse(courseId);
            if (response.success) {
                const course = response.data;
                setFormData({
                    code: course.code,
                    name: course.name,
                    description: course.description,
                    max_students: course.max_students,
                    enrollment_type: course.enrollment_type,
                    start_date: course.start_date.split('T')[0],
                    end_date: course.end_date.split('T')[0],
                    is_active: course.is_active
                });
            } else {
                setError(response.message || 'Failed to load course');
            }
        } catch (err) {
            console.error('Error fetching course:', err);
            setError('Failed to load course');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const response = isEditMode
                ? await courseApi.updateCourse(courseId, formData)
                : await courseApi.createCourse(formData);

            if (response.success) {
                toast.success(`Course ${isEditMode ? 'updated' : 'created'} successfully!`);
                navigate('/admin/courses');
            } else {
                setError(response.message || `Failed to ${isEditMode ? 'update' : 'create'} course`);
            }
        } catch (err) {
            console.error('Error saving course:', err);
            setError(err.message || `Failed to ${isEditMode ? 'update' : 'create'} course`);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading course...</div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="max-w-3xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-900">
                        {isEditMode ? 'Edit Course' : 'Create Course'}
                    </h1>
                    <button
                        onClick={() => navigate('/admin/courses')}
                        className="text-gray-600 hover:text-gray-800"
                    >
                        Cancel
                    </button>
                </div>

                {error && (
                    <div className="mb-6 bg-red-50 border border-red-200 text-red-600 rounded-lg p-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="grid grid-cols-1 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Course Code
                                </label>
                                <input
                                    type="text"
                                    name="code"
                                    value={formData.code}
                                    onChange={handleChange}
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Course Name
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Description
                                </label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    rows={4}
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Max Students
                                    </label>
                                    <input
                                        type="number"
                                        name="max_students"
                                        value={formData.max_students}
                                        onChange={handleChange}
                                        min={1}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Enrollment Type
                                    </label>
                                    <select
                                        name="enrollment_type"
                                        value={formData.enrollment_type}
                                        onChange={handleChange}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                    >
                                        <option value="open">Open</option>
                                        <option value="invite">Invite Only</option>
                                        <option value="closed">Closed</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Start Date
                                    </label>
                                    <input
                                        type="date"
                                        name="start_date"
                                        value={formData.start_date}
                                        onChange={handleChange}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        End Date
                                    </label>
                                    <input
                                        type="date"
                                        name="end_date"
                                        value={formData.end_date}
                                        onChange={handleChange}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleChange}
                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                                />
                                <label className="ml-2 text-sm text-gray-700">
                                    Course is active
                                </label>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end space-x-4">
                        <button
                            type="button"
                            onClick={() => navigate('/admin/courses')}
                            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            {isEditMode ? 'Update Course' : 'Create Course'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CourseForm; 