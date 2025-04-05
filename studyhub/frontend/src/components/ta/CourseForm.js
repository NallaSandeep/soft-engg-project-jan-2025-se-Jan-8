import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { toast } from 'react-hot-toast';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

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
        if (formData.start_date && formData.end_date) {
            const startDate = new Date(formData.start_date);
            const endDate = new Date(formData.end_date);
            if (endDate < startDate) {
                setError('End date cannot be before the start date.');
                return; // Prevent form submission
            }
        }
        try {
            setLoading(true);
            setError(null);
            
            let response;
            if (isEditMode) {
                response = await courseApi.updateCourse(courseId, formData);
            } else {
                response = await courseApi.createCourse(formData);
            }
            
            if (response.success) {
                toast.success(`Course ${isEditMode ? 'updated' : 'created'} successfully!`);
                navigate('/ta/courses');
            } else {
                setError(response.message || `Failed to ${isEditMode ? 'update' : 'create'} course`);
            }
        } catch (err) {
            console.error(`Error ${isEditMode ? 'updating' : 'creating'} course:`, err);
            setError(err.message || `Failed to ${isEditMode ? 'update' : 'create'} course`);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>
        );
    }

    return (
        <div>
            <div className="max-w-3xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                        {isEditMode ? 'Edit Course' : 'Create Course'}
                    </h1>
                    <button
                        onClick={() => navigate('/ta/courses')}
                        className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200 flex items-center gap-1"
                    >
                        <ArrowLeftIcon className="h-4 w-4" /> Back to Courses
                    </button>
                </div>

                {error && (
                    <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="glass-card p-6">
                        <div className="grid grid-cols-1 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Course Code
                                </label>
                                <input
                                    type="text"
                                    name="code"
                                    value={formData.code}
                                    onChange={handleChange}
                                    className="input-field"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Course Name
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="input-field"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Description
                                </label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    rows="4"
                                    className="input-field"
                                ></textarea>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        Max Students
                                    </label>
                                    <input
                                        type="number"
                                        name="max_students"
                                        value={formData.max_students}
                                        onChange={handleChange}
                                        min="1"
                                        className="input-field"
                                        required
                                    />
                                </div>

                                {/*<div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        Enrollment Type
                                    </label>
                                    <select
                                        name="enrollment_type"
                                        value={formData.enrollment_type}
                                        onChange={handleChange}
                                        className="input-field"
                                        required
                                    >
                                        <option value="open">Open</option>
                                        <option value="invite">Invite Only</option>
                                        <option value="closed">Closed</option>
                                    </select>
                                </div>*/}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        Start Date
                                    </label>
                                    <input
                                        type="date"
                                        name="start_date"
                                        value={formData.start_date}
                                        onChange={handleChange}
                                        className="input-field"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                        End Date
                                    </label>
                                    <input
                                        type="date"
                                        name="end_date"
                                        value={formData.end_date}
                                        onChange={handleChange}
                                        className="input-field"
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
                                    className="h-4 w-4 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400 rounded"
                                />
                                <label className="ml-2 text-sm text-zinc-700 dark:text-zinc-300">
                                    Course is active
                                </label>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end space-x-4">
                        <button
                            type="button"
                            onClick={() => navigate('/ta/courses')}
                            className="px-4 py-2 border border-zinc-300 dark:border-zinc-600 text-zinc-700 dark:text-zinc-300 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                        >
                            {isEditMode ? 'Update' : 'Create'} Course
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CourseForm; 