import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { toast } from 'react-hot-toast';
import 'bootstrap/dist/css/bootstrap.min.css';

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
        return <div className="text-center text-warning">Loading course...</div>;
    }

    return (
        <div className="container py-5 text-white" style={{ backgroundColor: '#121212', minHeight: '100vh' }}>
            <h1 className="text-warning mb-4">{isEditMode ? 'Edit Course' : 'Create Course'}</h1>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={handleSubmit} className="bg-dark p-4 rounded border border-warning">
                <div className="mb-3">
                    <label className="form-label text-warning">Course Code</label>
                    <input type="text" name="code" value={formData.code} onChange={handleChange} className="form-control bg-dark text-white border-warning" required />
                </div>
                <div className="mb-3">
                    <label className="form-label text-warning">Course Name</label>
                    <input type="text" name="name" value={formData.name} onChange={handleChange} className="form-control bg-dark text-white border-warning" required />
                </div>
                <div className="mb-3">
                    <label className="form-label text-warning">Description</label>
                    <textarea name="description" value={formData.description} onChange={handleChange} className="form-control bg-dark text-white border-warning" rows="3" />
                </div>
                <div className="row">
                    <div className="col-md-6 mb-3">
                        <label className="form-label text-warning">Max Students</label>
                        <input type="number" name="max_students" value={formData.max_students} onChange={handleChange} className="form-control bg-dark text-white border-warning" required />
                    </div>
                    <div className="col-md-6 mb-3">
                        <label className="form-label text-warning">Enrollment Type</label>
                        <select name="enrollment_type" value={formData.enrollment_type} onChange={handleChange} className="form-select bg-dark text-white border-warning">
                            <option value="open">Open</option>
                            <option value="invite">Invite Only</option>
                            <option value="closed">Closed</option>
                        </select>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-6 mb-3">
                        <label className="form-label text-warning">Start Date</label>
                        <input type="date" name="start_date" value={formData.start_date} onChange={handleChange} className="form-control bg-dark text-white border-warning" required />
                    </div>
                    <div className="col-md-6 mb-3">
                        <label className="form-label text-warning">End Date</label>
                        <input type="date" name="end_date" value={formData.end_date} onChange={handleChange} className="form-control bg-dark text-white border-warning" required />
                    </div>
                </div>
                <div className="form-check mb-3">
                    <input type="checkbox" name="is_active" checked={formData.is_active} onChange={handleChange} className="form-check-input border-warning" />
                    <label className="form-check-label text-warning">Course is active</label>
                </div>
                <div className="d-flex justify-content-end gap-3">
                    <button type="button" className="btn btn-outline-warning" onClick={() => navigate('/admin/courses')}>Cancel</button>
                    <button type="submit" className="btn btn-warning fw-bold">{isEditMode ? 'Update Course' : 'Create Course'}</button>
                </div>
            </form>
        </div>
    );
};

export default CourseForm;
