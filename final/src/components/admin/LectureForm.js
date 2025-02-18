import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import 'bootstrap/dist/css/bootstrap.min.css';

const LectureForm = ({ mode = 'create' }) => {
    const navigate = useNavigate();
    const { courseId, weekId, lectureId } = useParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lectureData, setLectureData] = useState({
        title: '',
        description: '',
        youtube_url: '',
        is_published: false
    });

    useEffect(() => {
        if (mode === 'edit' && lectureId) {
            fetchLectureData();
        } else {
            setLoading(false);
        }
    }, [mode, lectureId]);

    const fetchLectureData = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getLectureContent(lectureId);
            if (response.success) {
                setLectureData({
                    title: response.data.title,
                    description: response.data.description || '',
                    youtube_url: response.data.youtube_url,
                    is_published: response.data.is_published
                });
            } else {
                setError(response.message || 'Failed to load lecture data');
            }
        } catch (err) {
            console.error('Error loading lecture data:', err);
            setError('Failed to load lecture data');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            let response;
            if (mode === 'edit') {
                response = await courseApi.updateLecture(lectureId, lectureData);
            } else {
                response = await courseApi.createLecture(weekId, lectureData);
            }

            if (response.success) {
                navigate(`/admin/courses/${courseId}/content`);
            } else {
                setError(response.message || `Failed to ${mode} lecture`);
            }
        } catch (err) {
            console.error(`Error ${mode}ing lecture:`, err);
            setError(`Failed to ${mode} lecture`);
        }
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100 text-warning">
                Loading lecture data...
            </div>
        );
    }

    if (error) {
        return (
            <div className="container p-4">
                <div className="alert alert-danger">{error}</div>
                <button
                    className="btn btn-outline-warning mt-3"
                    onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                >
                    ← Back to Course Content
                </button>
            </div>
        );
    }

    return (
        <div className="container-fluid p-4 text-white" style={{ backgroundColor: '#121212', minHeight: '100vh' }}>
            {/* Breadcrumb Navigation */}
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <button className="btn btn-outline-warning btn-sm" onClick={() => navigate(`/admin/courses/${courseId}/content`)}>
                        ← Back to Course Content
                    </button>
                    <h1 className="mt-3 text-warning">{mode === 'edit' ? 'Edit Lecture' : 'Add New Lecture'}</h1>
                </div>
            </div>

            {/* Lecture Form */}
            <div className="card bg-dark text-white p-4">
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label className="form-label text-warning">Title</label>
                        <input
                            type="text"
                            value={lectureData.title}
                            onChange={(e) => setLectureData(prev => ({ ...prev, title: e.target.value }))}
                            className="form-control bg-secondary text-white"
                            required
                        />
                    </div>

                    <div className="mb-3">
                        <label className="form-label text-warning">Description</label>
                        <textarea
                            value={lectureData.description}
                            onChange={(e) => setLectureData(prev => ({ ...prev, description: e.target.value }))}
                            className="form-control bg-secondary text-white"
                            rows="4"
                        />
                    </div>

                    <div className="mb-3">
                        <label className="form-label text-warning">YouTube URL</label>
                        <input
                            type="url"
                            value={lectureData.youtube_url}
                            onChange={(e) => setLectureData(prev => ({ ...prev, youtube_url: e.target.value }))}
                            className="form-control bg-secondary text-white"
                            required
                            placeholder="https://www.youtube.com/watch?v=..."
                        />
                    </div>

                    <div className="form-check mb-3">
                        <input
                            type="checkbox"
                            id="is_published"
                            checked={lectureData.is_published}
                            onChange={(e) => setLectureData(prev => ({ ...prev, is_published: e.target.checked }))}
                            className="form-check-input bg-warning"
                        />
                        <label htmlFor="is_published" className="form-check-label text-white">
                            Published
                        </label>
                    </div>

                    <div className="d-flex justify-content-end gap-3">
                        <button
                            type="button"
                            onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                            className="btn btn-outline-light"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn-warning"
                        >
                            {mode === 'edit' ? 'Save Changes' : 'Create Lecture'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default LectureForm;
