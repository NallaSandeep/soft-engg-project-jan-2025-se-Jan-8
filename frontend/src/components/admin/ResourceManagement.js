import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi, resourceApi } from '../../services/apiService';

const ResourceManagement = () => {
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
        type: 'file',
        content: '',
        file_path: '',
        file_type: '',
        file_size: 0,
        is_active: true,
        is_public: false
    });
    const [selectedFile, setSelectedFile] = useState(null);
    const [resources, setResources] = useState([]);
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

    const fetchResources = async () => {
        try {
            setError(null);
            const response = await resourceApi.getResources(selectedCourse.id);
            console.log('Resources response:', response); // Debug log
            if (response.success && response.data?.resources) {
                setResources(response.data.resources);
            } else {
                setError(response.message || 'Failed to load resources: Invalid response format');
            }
        } catch (err) {
            console.error('Error loading resources:', err);
            setError(err.message || 'Failed to load resources');
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

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
            setFormData(prev => ({
                ...prev,
                file_type: file.type,
                file_size: file.size,
                file_path: file.name
            }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setFormError(null);
            const formDataToSend = new FormData();
            Object.keys(formData).forEach(key => {
                formDataToSend.append(key, formData[key]);
            });
            if (selectedFile) {
                formDataToSend.append('file', selectedFile);
            }

            const response = await courseApi.createResource(formDataToSend);
            if (response.success) {
                setShowAddForm(false);
                setFormData({
                    week_id: '',
                    title: '',
                    description: '',
                    type: 'file',
                    content: '',
                    file_path: '',
                    file_type: '',
                    file_size: 0,
                    is_active: true,
                    is_public: false
                });
                setSelectedFile(null);
                fetchCourses();
            } else {
                setFormError(response.error || 'Failed to create resource');
            }
        } catch (err) {
            setFormError(err.message || 'Failed to create resource');
            console.error('Error creating resource:', err);
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
                <h1 className="text-2xl font-bold">Resource Management</h1>
                <button
                    onClick={() => setShowAddForm(true)}
                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                >
                    Add New Resource
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

            {/* Add Resource Form */}
            {showAddForm && selectedCourse && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">Add New Resource</h2>
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
                                <option value="file">File</option>
                                <option value="link">Link</option>
                                <option value="text">Text</option>
                            </select>
                        </div>
                        {formData.type === 'file' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700">File</label>
                                <input
                                    type="file"
                                    onChange={handleFileChange}
                                    className="mt-1 block w-full"
                                    required
                                />
                            </div>
                        )}
                        {formData.type === 'link' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700">URL</label>
                                <input
                                    type="url"
                                    name="content"
                                    value={formData.content}
                                    onChange={handleInputChange}
                                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                    required
                                />
                            </div>
                        )}
                        {formData.type === 'text' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Content</label>
                                <textarea
                                    name="content"
                                    value={formData.content}
                                    onChange={handleInputChange}
                                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                    rows="5"
                                    required
                                />
                            </div>
                        )}
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleInputChange}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label className="ml-2 block text-sm text-gray-900">
                                    Active
                                </label>
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    name="is_public"
                                    checked={formData.is_public}
                                    onChange={handleInputChange}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label className="ml-2 block text-sm text-gray-900">
                                    Public
                                </label>
                            </div>
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
                                Create Resource
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Resource List */}
            {selectedCourse && (
                <div className="space-y-6">
                    {selectedCourse.weeks?.map(week => (
                        <div key={week.id} className="bg-white rounded-lg shadow">
                            <div className="p-6 border-b border-gray-200">
                                <h2 className="text-xl font-semibold">Week {week.number}: {week.title}</h2>
                            </div>
                            <div className="p-6">
                                {week.resources?.length > 0 ? (
                                    <div className="space-y-4">
                                        {week.resources.map(resource => (
                                            <div
                                                key={resource.id}
                                                className="flex justify-between items-start p-4 bg-gray-50 rounded-lg"
                                            >
                                                <div>
                                                    <h3 className="font-medium">{resource.title}</h3>
                                                    <p className="text-sm text-gray-600 mt-1">{resource.description}</p>
                                                    <div className="mt-2 space-x-2">
                                                        <span className={`px-2 py-1 rounded text-xs ${
                                                            resource.type === 'file'
                                                                ? 'bg-blue-100 text-blue-800'
                                                                : resource.type === 'link'
                                                                ? 'bg-green-100 text-green-800'
                                                                : 'bg-yellow-100 text-yellow-800'
                                                        }`}>
                                                            {resource.type.charAt(0).toUpperCase() + resource.type.slice(1)}
                                                        </span>
                                                        <span className={`px-2 py-1 rounded text-xs ${
                                                            resource.is_active
                                                                ? 'bg-green-100 text-green-800'
                                                                : 'bg-red-100 text-red-800'
                                                        }`}>
                                                            {resource.is_active ? 'Active' : 'Inactive'}
                                                        </span>
                                                        <span className={`px-2 py-1 rounded text-xs ${
                                                            resource.is_public
                                                                ? 'bg-green-100 text-green-800'
                                                                : 'bg-yellow-100 text-yellow-800'
                                                        }`}>
                                                            {resource.is_public ? 'Public' : 'Private'}
                                                        </span>
                                                    </div>
                                                </div>
                                                {resource.type === 'file' && (
                                                    <div className="text-sm text-gray-600">
                                                        <p>Size: {(resource.file_size / 1024).toFixed(2)} KB</p>
                                                        <p>Type: {resource.file_type}</p>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-gray-600 text-center">No resources available for this week.</p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ResourceManagement; 