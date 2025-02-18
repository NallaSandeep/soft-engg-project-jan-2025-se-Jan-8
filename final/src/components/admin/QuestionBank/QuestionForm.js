import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { questionBankApi, courseApi } from '../../../services/apiService';

const QuestionForm = ({ mode = 'create' }) => {
    const { questionId } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [courses, setCourses] = useState([]);
    const [formData, setFormData] = useState({
        title: '',
        content: '',
        type: 'MCQ',
        options: ['', ''],
        correct_answer: '',
        points: 1,
        explanation: '',
        course_id: '',
        status: 'draft'
    });

    const curr_courses = [
        { id: 'CS101', name: 'Introduction to Programming' },
        { id: 'CS102', name: 'Data Structures' },
        { id: 'ML101', name: 'Introduction to ML' }
    ];

    const isViewMode = mode === 'view';

    useEffect(() => {
        //fetchCourses();
        if (questionId) fetchQuestion();
        else setLoading(false);
    }, [questionId]);

    const fetchCourses = async () => {
        try {
            const response = await courseApi.getCourses();
            if (response.success) {
                setCourses(response.data || []);
            } else {
                setError(response.message || 'Failed to load courses');
            }
        } catch (err) {
            setError('Error fetching courses');
            console.error('Error fetching courses:', err);
        }
    };

    const fetchQuestion = async () => {
        try {
            setLoading(true);
            const response = await questionBankApi.getQuestion(questionId);
            if (response.success) {
                setFormData({ ...response.data });
            } else {
                setError(response.message || 'Failed to load question');
            }
        } catch (err) {
            setError('Error fetching question');
            console.error('Error fetching question:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleOptionChange = (index, value) => {
        setFormData(prev => {
            const updatedOptions = [...prev.options];
            updatedOptions[index] = value;
            return { ...prev, options: updatedOptions };
        });
    };

    const addOption = () => {
        setFormData(prev => ({ ...prev, options: [...prev.options, ''] }));
    };

    const removeOption = (index) => {
        setFormData(prev => {
            const updatedOptions = prev.options.filter((_, i) => i !== index);
            return { ...prev, options: updatedOptions };
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.title || !formData.content || !formData.course_id) {
            setError('Please fill in all required fields');
            return;
        }

        try {
            const response = questionId 
                ? await questionBankApi.updateQuestion(questionId, formData)
                : await questionBankApi.createQuestion(formData);

            if (response.success) {
                navigate('/admin/question-bank');
            } else {
                setError(response.message || 'Failed to save question');
            }
        } catch (err) {
            setError('Error saving question');
            console.error('Error saving question:', err);
        }
    };

    if (loading) return <div className="text-center text-light">Loading...</div>;

    return (
        <div className="container text-light p-4 bg-dark rounded shadow-lg">
            <h2 className="text-warning mb-4">
                {isViewMode ? 'View Question' : questionId ? 'Edit Question' : 'Create New Question'}
            </h2>
            {error && <div className="alert alert-danger">{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Title</label>
                    <input 
                        type="text" 
                        name="title" 
                        value={formData.title} 
                        onChange={handleInputChange} 
                        className="form-control bg-dark text-light border-secondary" 
                        disabled={isViewMode} 
                        required 
                    />
                </div>

                <div className="mb-3">
                    <label className="form-label">Question Text</label>
                    <textarea 
                        name="content" 
                        value={formData.content} 
                        onChange={handleInputChange} 
                        className="form-control bg-dark text-light border-secondary" 
                        rows="3" 
                        disabled={isViewMode} 
                        required
                    ></textarea>
                </div>

                <div className="mb-3">
                    <label className="form-label">Course</label>
                    <select name="course_id" value={formData.course_id} onChange={handleInputChange} className="form-select bg-dark text-light border-secondary" disabled={isViewMode} required>
                        <option value="">Select Course</option>
                        {curr_courses.map(course => (
                            <option key={course.id} value={course.id}>{course.name}</option>
                        ))}
                    </select>
                </div>

                {formData.type === 'MCQ' && (
                    <div className="mb-3">
                        <label className="form-label">Options</label>
                        {formData.options.map((option, index) => (
                            <div key={index} className="d-flex mb-2">
                                <input 
                                    type="text" 
                                    value={option} 
                                    onChange={(e) => handleOptionChange(index, e.target.value)} 
                                    className="form-control bg-dark text-light border-secondary me-2" 
                                    disabled={isViewMode} 
                                    required 
                                />
                                {!isViewMode && formData.options.length > 2 && (
                                    <button 
                                        type="button" 
                                        className="btn btn-danger" 
                                        onClick={() => removeOption(index)}
                                    >X</button>
                                )}
                            </div>
                        ))}
                        {!isViewMode && (
                            <button type="button" className="btn btn-warning mt-2" onClick={addOption}>
                                Add Option
                            </button>
                        )}
                    </div>
                )}

                <div className="mb-3">
                    <label className="form-label">Correct Answer</label>
                    <input 
                        type="text" 
                        name="correct_answer" 
                        value={formData.correct_answer} 
                        onChange={handleInputChange} 
                        className="form-control bg-dark text-light border-secondary" 
                        disabled={isViewMode} 
                        required 
                    />
                </div>

                {!isViewMode && (
                    <div className="d-flex justify-content-end">
                        <button type="button" className="btn btn-outline-light me-2" onClick={() => navigate('/admin/question-bank')}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-warning">
                            {questionId ? 'Update Question' : 'Create Question'}
                        </button>
                    </div>
                )}
            </form>
        </div>
    );
};

export default QuestionForm;
