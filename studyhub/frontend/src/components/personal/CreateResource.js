import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { personalApi, courseApi } from '../../services/apiService';
import { Button } from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';

const Modal = ({ children, onClose }) => {
    useEffect(() => {
        // Prevent body scrolling when modal is open
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, []);

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
                <div className="fixed inset-0 transition-opacity" onClick={onClose}>
                    <div className="absolute inset-0 bg-gray-500 opacity-75 dark:bg-gray-900"></div>
                </div>
                <div className="relative inline-block w-full max-w-lg p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-zinc-800 shadow-xl rounded-lg">
                    {children}
                </div>
            </div>
        </div>
    );
};

const CreateResource = ({ onClose, onSuccess }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [courseId, setCourseId] = useState('');
    const [courses, setCourses] = useState([]);
    const [loadingCourses, setLoadingCourses] = useState(true);

    useEffect(() => {
        loadEnrolledCourses();
    }, []);

    const loadEnrolledCourses = async () => {
        try {
            setLoadingCourses(true);
            const response = await courseApi.getCourses();
            setCourses(response.data || []);
        } catch (err) {
            console.error('Failed to load courses:', err);
            setError('Failed to load enrolled courses');
        } finally {
            setLoadingCourses(false);
        }
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!name.trim()) {
            setError('Name is required');
            return false;
        }

        if (!courseId) {
            setError('Please select a course');
            return false;
        }

        try {
            setLoading(true);
            setError(null);
            const payload = {
                name: name.trim(),
                description: description.trim(),
                course_id: courseId
            };
            console.log('Sending payload:', payload);
            await personalApi.createPersonalResource(payload);
            onSuccess?.();
            onClose?.();
            return true;
        } catch (err) {
            console.error('Error response:', err.response?.data);
            setError(err.response?.data?.message || err.message || 'Failed to create resource');
            return false;
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Create New Resource</h2>
            {error && <ErrorAlert message={error} className="mb-4" />}
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300" htmlFor="courseId">
                        Course *
                    </label>
                    {loadingCourses ? (
                        <div className="flex items-center space-x-2 p-2">
                            <LoadingSpinner size="sm" />
                            <span className="text-sm text-gray-500">Loading courses...</span>
                        </div>
                    ) : (
                        <select
                            id="courseId"
                            value={courseId}
                            onChange={(e) => setCourseId(e.target.value)}
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 bg-white dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                            required
                        >
                            <option value="">Select a course</option>
                            {courses.map(course => (
                                <option key={course.id} value={course.id}>
                                    {course.code} - {course.name}
                                </option>
                            ))}
                        </select>
                    )}
                </div>
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300" htmlFor="name">
                        Name *
                    </label>
                    <input
                        id="name"
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 bg-white dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                        placeholder="Enter resource name"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300" htmlFor="description">
                        Description
                    </label>
                    <textarea
                        id="description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 bg-white dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                        placeholder="Enter resource description"
                        rows={3}
                    />
                </div>
                <div className="flex justify-end space-x-2">
                    <Button type="button" variant="secondary" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button type="submit" disabled={loading || loadingCourses}>
                        {loading ? <LoadingSpinner size="sm" /> : 'Create Resource'}
                    </Button>
                </div>
            </form>
        </>
    );
};

export const showCreateResource = () => {
    return new Promise((resolve) => {
        const modalContainer = document.createElement('div');
        modalContainer.id = 'create-resource-modal';
        document.body.appendChild(modalContainer);

        const root = createRoot(modalContainer);

        const handleClose = () => {
            root.unmount();
            document.body.removeChild(modalContainer);
            resolve(false);
        };

        const handleSuccess = () => {
            root.unmount();
            document.body.removeChild(modalContainer);
            resolve(true);
        };

        root.render(
            <Modal onClose={handleClose}>
                <CreateResource onClose={handleClose} onSuccess={handleSuccess} />
            </Modal>
        );
    });
};

export default CreateResource; 