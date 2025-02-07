import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';

const ResourceManagement = () => {
    const [resources, setResources] = useState([]);
    const [file, setFile] = useState(null);
    const [docTitle, setDocTitle] = useState('');
    const [includeInAI, setIncludeInAI] = useState(false);
    const [courseId, setCourseId] = useState('');
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        fetchResources();
        fetchCourses();
    }, []);

    const fetchResources = async () => {
        try {
            setLoading(true);
            const response = await apiService.getResources();
            setResources(response.data);
            setError('');
        } catch (err) {
            console.error('Error fetching resources:', err);
            setError('Failed to fetch resources. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const fetchCourses = async () => {
        try {
            const response = await apiService.getCourses();
            setCourses(response.data);
        } catch (err) {
            console.error('Error fetching courses:', err);
        }
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        if (selectedFile && !docTitle) {
            setDocTitle(selectedFile.name);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file to upload');
            return;
        }

        try {
            setLoading(true);
            setError('');

            const formData = new FormData();
            formData.append('file', file);
            formData.append('doc_title', docTitle || file.name);
            formData.append('included_in_ai', includeInAI);
            if (courseId) {
                formData.append('course_id', courseId);
            }

            await apiService.uploadResource(formData);

            setSuccessMessage('Resource uploaded successfully!');
            setFile(null);
            setDocTitle('');
            setIncludeInAI(false);
            setCourseId('');

            // Refresh the resources list
            fetchResources();

            // Clear success message after 3 seconds
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            console.error('Error uploading resource:', err);
            setError('Failed to upload resource. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
            <h2>Resource Management</h2>

            {/* Upload Form */}
            <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
                <h3>Upload New Resource</h3>
                {error && (
                    <div style={{ color: 'red', marginBottom: '10px', padding: '10px', backgroundColor: '#ffebee', borderRadius: '4px' }}>
                        {error}
                    </div>
                )}
                {successMessage && (
                    <div style={{ color: 'green', marginBottom: '10px', padding: '10px', backgroundColor: '#e8f5e9', borderRadius: '4px' }}>
                        {successMessage}
                    </div>
                )}
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '15px' }}>
                        <input
                            type="file"
                            onChange={handleFileChange}
                            style={{ marginBottom: '10px' }}
                            disabled={loading}
                        />
                    </div>
                    <div style={{ marginBottom: '15px' }}>
                        <input
                            type="text"
                            placeholder="Document Title"
                            value={docTitle}
                            onChange={(e) => setDocTitle(e.target.value)}
                            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                            disabled={loading}
                        />
                    </div>
                    <div style={{ marginBottom: '15px' }}>
                        <select
                            value={courseId}
                            onChange={(e) => setCourseId(e.target.value)}
                            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                            disabled={loading}
                        >
                            <option value="">Select Course (Optional)</option>
                            {courses.map(course => (
                                <option key={course.id} value={course.id}>
                                    {course.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={includeInAI}
                                onChange={(e) => setIncludeInAI(e.target.checked)}
                                style={{ marginRight: '8px' }}
                                disabled={loading}
                            />
                            Include in AI Training
                        </label>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            padding: '10px 20px',
                            backgroundColor: loading ? '#ccc' : '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: loading ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {loading ? 'Uploading...' : 'Upload Resource'}
                    </button>
                </form>
            </div>

            {/* Resources List */}
            <div>
                <h3>Your Resources</h3>
                {loading && <p>Loading resources...</p>}
                {resources.length === 0 ? (
                    <p>No resources found.</p>
                ) : (
                    <div style={{ display: 'grid', gap: '15px' }}>
                        {resources.map(resource => (
                            <div
                                key={resource.id}
                                style={{
                                    padding: '15px',
                                    border: '1px solid #ddd',
                                    borderRadius: '4px',
                                    backgroundColor: 'white'
                                }}
                            >
                                <h4 style={{ margin: '0 0 10px 0' }}>{resource.doc_title}</h4>
                                <p style={{ margin: '0', color: '#666', fontSize: '0.9em' }}>
                                    Type: {resource.doc_type.toUpperCase()}
                                </p>
                                <p style={{ margin: '5px 0', color: '#666', fontSize: '0.9em' }}>
                                    Uploaded: {new Date(resource.created_at).toLocaleDateString()}
                                </p>
                                {resource.course_id && (
                                    <p style={{ margin: '5px 0', color: '#666', fontSize: '0.9em' }}>
                                        Course: {courses.find(c => c.id === resource.course_id)?.name || 'Unknown'}
                                    </p>
                                )}
                                {resource.included_in_ai && (
                                    <span style={{
                                        backgroundColor: '#e3f2fd',
                                        color: '#1976d2',
                                        padding: '2px 8px',
                                        borderRadius: '12px',
                                        fontSize: '0.8em'
                                    }}>
                                        AI Enabled
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResourceManagement; 