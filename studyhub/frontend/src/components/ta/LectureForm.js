import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const LectureForm = ({ mode = 'create' }) => {
    const navigate = useNavigate();
    const { courseId, weekId, lectureId } = useParams();
    const [loading, setLoading] = useState(false);
    const [formSubmitting, setFormSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        youtube_url: '',
        transcript: '',
        is_published: false,
        lecture_number: 1,
        content_type: 'youtube' // Add default content type
    });

    // Fetch lecture data when in edit mode
    useEffect(() => {
        if (mode === 'edit' && lectureId) {
            fetchLecture();
        }
    }, [lectureId, mode]);

    const fetchLecture = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getLectureContent(lectureId);
            if (response.success) {
                const lecture = response.data;
                setFormData({
                    title: lecture.title || '',
                    description: lecture.description || '',
                    youtube_url: lecture.youtube_url || '',
                    transcript: lecture.transcript || '',
                    is_published: lecture.is_published || false,
                    lecture_number: lecture.lecture_number || 1,
                    content_type: lecture.content_type || 'youtube' // Add content_type
                });
            } else {
                setError(response.message || 'Failed to load lecture');
            }
        } catch (err) {
            console.error('Error fetching lecture:', err);
            setError('Failed to load lecture details');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : 
                   (name === 'lecture_number' ? parseInt(value, 10) : value)
        }));
    };

    const validateForm = () => {
        const errors = [];
        if (!formData.title.trim()) {
            errors.push('Title is required');
        }
        if (!formData.youtube_url.trim()) {
            errors.push('YouTube URL is required');
        }
        if (!formData.lecture_number || formData.lecture_number < 1) {
            errors.push('Lecture number is required and must be at least 1');
        }
        
        return errors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const validationErrors = validateForm();
        
        if (validationErrors.length > 0) {
            setError(validationErrors.join(', '));
            return;
        }

        try {
            setFormSubmitting(true);
            setError(null);
            
            // Log the data being sent
            console.log('Creating lecture with data:', { weekId, formData });
            
            let response;
            if (mode === 'create') {
                response = await courseApi.createLecture(weekId, formData);
            } else {
                response = await courseApi.updateLecture(lectureId, formData);
            }

            console.log('API response:', response);

            if (response.success) {
                setSuccess(`Lecture ${mode === 'create' ? 'created' : 'updated'} successfully!`);
                setTimeout(() => {
                    navigate(`/ta/courses/${courseId}/content`);
                }, 1500);
            } else {
                // Display specific message for duplicate lecture number
                if (response.message && response.message.includes('already exists')) {
                    setError(`Lecture number ${formData.lecture_number} already exists. Please choose a different lecture number.`);
                } else {
                    setError(response.message || `Failed to ${mode} lecture`);
                }
            }
        } catch (err) {
            console.error(`Error ${mode === 'create' ? 'creating' : 'updating'} lecture:`, err);
            // Check for unique constraint error in error message
            if (err.message && err.message.includes('already exists')) {
                setError(`Lecture number ${formData.lecture_number} already exists. Please choose a different lecture number.`);
            } else {
                // Show more detailed error information
                const errorMessage = err.message || 'Unknown error';
                const errorDetails = err.error ? `: ${err.error}` : '';
                setError(`Failed to ${mode} lecture. ${errorMessage}${errorDetails}`);
            }
        } finally {
            setFormSubmitting(false);
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
        <div className="p-6">
            <div className="flex items-center mb-6">
                <button
                    onClick={() => navigate(`/ta/courses/${courseId}/content`)}
                    className="text-zinc-600 dark:text-zinc-400 hover:text-blue-600 dark:hover:text-blue-400 mr-2"
                >
                    <ArrowLeftIcon className="h-5 w-5" />
                </button>
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                    {mode === 'create' ? 'Add New Lecture' : 'Edit Lecture'}
                </h1>
            </div>
            
            {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 p-4 rounded-lg mb-6">
                    {error}
                </div>
            )}
            
            {success && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 p-4 rounded-lg mb-6">
                    {success}
                </div>
            )}
            
            <form onSubmit={handleSubmit} className="glass-card p-6 space-y-6">
                <div>
                    <label htmlFor="lecture_number" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                        Lecture Number *
                    </label>
                    <input
                        type="number"
                        id="lecture_number"
                        name="lecture_number"
                        min="1"
                        value={formData.lecture_number}
                        onChange={handleInputChange}
                        className="block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-4 py-2 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                        required
                    />
                    <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                        Lecture ordering within the week
                    </p>
                </div>

                <div>
                    <label htmlFor="title" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                        Lecture Title *
                    </label>
                    <input
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
                        className="block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-4 py-2 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                        required
                    />
                </div>
                
                <div>
                    <label htmlFor="description" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                        Description
                    </label>
                    <textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleInputChange}
                        rows="3"
                        className="block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-4 py-2 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                    />
                </div>
                
                <div>
                    <label htmlFor="youtube_url" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                        YouTube URL *
                    </label>
                    <input
                        type="url"
                        id="youtube_url"
                        name="youtube_url"
                        value={formData.youtube_url}
                        onChange={handleInputChange}
                        placeholder="https://www.youtube.com/watch?v=example"
                        className="block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-4 py-2 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                        required
                    />
                    <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                        Enter the full YouTube URL (e.g., https://www.youtube.com/watch?v=example)
                    </p>
                </div>
                
                <div>
                    <label htmlFor="transcript" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                        Transcript
                    </label>
                    <textarea
                        id="transcript"
                        name="transcript"
                        value={formData.transcript}
                        onChange={handleInputChange}
                        rows="5"
                        className="block w-full rounded-md border border-zinc-300 dark:border-zinc-700 px-4 py-2 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                    />
                    <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                        Optional: Add a transcript of the lecture for accessibility
                    </p>
                </div>
                
                <div className="flex items-center">
                    <input
                        type="checkbox"
                        id="is_published"
                        name="is_published"
                        checked={formData.is_published}
                        onChange={handleInputChange}
                        className="rounded border-zinc-300 dark:border-zinc-700 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400 h-4 w-4"
                    />
                    <label htmlFor="is_published" className="ml-2 block text-sm text-zinc-700 dark:text-zinc-300">
                        Publish lecture (visible to students)
                    </label>
                </div>
                
                <div className="flex justify-end space-x-4 pt-4">
                    <button
                        type="button"
                        onClick={() => navigate(`/ta/courses/${courseId}/content`)}
                        className="px-4 py-2 text-sm font-medium text-zinc-700 dark:text-zinc-300 bg-zinc-200 dark:bg-zinc-700 rounded-md hover:bg-zinc-300 dark:hover:bg-zinc-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-zinc-500 dark:focus:ring-zinc-400"
                        disabled={formSubmitting}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-700 rounded-md hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                        disabled={formSubmitting}
                    >
                        {formSubmitting ? (
                            <>
                                <span className="inline-block animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></span>
                                {mode === 'create' ? 'Creating...' : 'Updating...'}
                            </>
                        ) : (
                            mode === 'create' ? 'Create Lecture' : 'Update Lecture'
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default LectureForm;