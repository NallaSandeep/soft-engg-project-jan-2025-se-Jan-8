import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { 
    PlusCircleIcon,
    AcademicCapIcon,
    PencilSquareIcon,
    DocumentTextIcon
} from '@heroicons/react/24/outline';

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

    const ActionButton = ({ label, icon: Icon, onClick, color = 'blue' }) => {
        const colorClasses = {
            blue: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white',
            green: 'bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-700 dark:hover:bg-emerald-600 text-white',
            gray: 'bg-zinc-600 hover:bg-zinc-700 dark:bg-zinc-700 dark:hover:bg-zinc-600 text-white'
        };
    
        return (
            <button
                onClick={onClick}
                className={`flex items-center justify-center space-x-2 px-4 py-2 rounded-lg ${colorClasses[color]} shadow-sm hover:shadow-md transition-shadow`}
            >
                <Icon className="w-5 h-5" />
                <span>{label}</span>
            </button>
        );
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading courses...</span>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold mb-6 text-zinc-900 dark:text-white">Course Management</h1>
                {/* <ActionButton 
                    label="Add New Course" 
                    icon={PlusCircleIcon} 
                    onClick={() => setShowAddForm(true)}
                    color="green"
                /> */}
            </div>

            {error && (
                <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Error!</strong>
                    <span className="block sm:inline"> {error}</span>
                </div>
            )}

            {/* Add Course Form */}
            {showAddForm && (
                <div className="glass-card p-6 mb-6 shadow-md dark:shadow-zinc-800/30">
                    <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Add New Course</h2>
                    {formError && (
                        <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded mb-4">
                            {formError}
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">Course Code</label>
                            <input
                                type="text"
                                name="code"
                                value={formData.code}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-2 bg-white dark:bg-zinc-800 shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 text-zinc-900 dark:text-white"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">Course Name</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-2 bg-white dark:bg-zinc-800 shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 text-zinc-900 dark:text-white"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">Description</label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-2 bg-white dark:bg-zinc-800 shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 text-zinc-900 dark:text-white"
                                rows="3"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">Max Students</label>
                            <input
                                type="number"
                                name="max_students"
                                value={formData.max_students}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-2 bg-white dark:bg-zinc-800 shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 text-zinc-900 dark:text-white"
                                min="1"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">Enrollment Type</label>
                            <select
                                name="enrollment_type"
                                value={formData.enrollment_type}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-2 bg-white dark:bg-zinc-800 shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 text-zinc-900 dark:text-white"
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
                                className="bg-zinc-300 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 px-4 py-2 rounded hover:bg-zinc-400 dark:hover:bg-zinc-600 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white px-4 py-2 rounded shadow-sm hover:shadow-md transition-shadow"
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
                        <div key={course.id} className="glass-card p-6 hover:shadow-lg transition-shadow">
                            <div className="flex justify-between items-start">
                                <div className="flex items-start gap-3">
                                    <AcademicCapIcon className="w-6 h-6 text-blue-500 dark:text-blue-400" />
                                    <div>
                                        <h2 className="text-xl font-semibold mb-2 text-zinc-900 dark:text-white">{course.name}</h2>
                                        <p className="text-zinc-600 dark:text-zinc-400 mb-2">{course.code}</p>
                                        <p className="text-zinc-700 dark:text-zinc-300 mb-4">{course.description}</p>
                                        <div className="text-sm text-zinc-600 dark:text-zinc-400">
                                            <p>Max Students: {course.max_students || 'Unlimited'}</p>
                                            <p className="flex items-center">
                                                <span>Enrollment:</span>
                                                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                                                    course.enrollment_type === 'open'
                                                        ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400'
                                                        : course.enrollment_type === 'closed'
                                                            ? 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400'
                                                            : 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400'
                                                }`}>
                                                    {course.enrollment_type}
                                                </span>
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                <div className="space-x-2 flex">
                                    <ActionButton
                                        label="Manage Content"
                                        icon={DocumentTextIcon}
                                        onClick={() => navigate(`/ta/courses/${course.id}/content`)}
                                        color="blue"
                                    />
                                    {/* <ActionButton
                                        label="Edit Course"
                                        icon={PencilSquareIcon}
                                        onClick={() => navigate(`/ta/courses/${course.id}/edit`)}
                                        color="gray"
                                    /> */}
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="glass-card p-8 text-center">
                        <AcademicCapIcon className="w-12 h-12 text-zinc-400 dark:text-zinc-500 mx-auto mb-4" />
                        <p className="text-zinc-600 dark:text-zinc-400">No courses available. Create your first course!</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseManagement;