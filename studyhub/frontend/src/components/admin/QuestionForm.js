import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { questionApi, courseApi } from '../../services/apiService';
import { FaPlus, FaTrash } from 'react-icons/fa';

const QuestionForm = ({ mode = 'create' }) => {
    const navigate = useNavigate();
    const { questionId } = useParams();
    const isViewMode = mode === 'view';
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [courses, setCourses] = useState([]);
    const [formData, setFormData] = useState({
        title: '',
        content: '',
        type: 'mcq',
        difficulty: 'medium',
        points: 1,
        options: [{ text: '', is_correct: false }, { text: '', is_correct: false }],
        correct_answer: '',
        explanation: '',
        course_id: '',
        status: 'active'
    });

    useEffect(() => {
        const fetchCourses = async () => {
            try {
                const response = await courseApi.getCourses();
                setCourses(response.data || []);
            } catch (err) {
                console.error('Error fetching courses:', err);
            }
        };

        fetchCourses();

        if (questionId && mode !== 'create') {
            fetchQuestion();
        } else {
            setLoading(false);
        }
    }, [questionId, mode]);

    const fetchQuestion = async () => {
        try {
            setLoading(true);
            const response = await questionApi.getQuestion(questionId);
            if (response.data) {
                // Ensure options array is properly formatted
                let options = response.data.options || [];
                if (typeof options === 'string') {
                    try {
                        options = JSON.parse(options);
                    } catch (e) {
                        options = [];
                    }
                }

                // Ensure we have at least 2 options for MCQ
                if (response.data.type === 'mcq' && options.length < 2) {
                    options = [
                        ...options,
                        ...Array(2 - options.length).fill().map(() => ({ text: '', is_correct: false }))
                    ];
                }

                setFormData({
                    ...response.data,
                    options
                });
            }
        } catch (err) {
            console.error('Error fetching question:', err);
            setError('Failed to load question');
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

    const handleOptionChange = (index, field, value) => {
        const newOptions = [...formData.options];
        newOptions[index] = { ...newOptions[index], [field]: value };
        
        // For MCQ, only one option can be correct
        if (formData.type === 'mcq' && field === 'is_correct' && value === true) {
            newOptions.forEach((option, i) => {
                if (i !== index) {
                    option.is_correct = false;
                }
            });
        }
        
        setFormData(prev => ({
            ...prev,
            options: newOptions
        }));
    };

    const addOption = () => {
        setFormData(prev => ({
            ...prev,
            options: [...prev.options, { text: '', is_correct: false }]
        }));
    };

    const removeOption = (index) => {
        if (formData.options.length <= 2) {
            return; // Maintain at least 2 options for MCQ
        }
        
        const newOptions = formData.options.filter((_, i) => i !== index);
        setFormData(prev => ({
            ...prev,
            options: newOptions
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            setLoading(true);
            
            // For MCQ, ensure at least one option is marked as correct
            if (formData.type === 'mcq' && !formData.options.some(opt => opt.is_correct)) {
                setError('Please mark at least one option as correct');
                setLoading(false);
                return;
            }
            
            // For text/numeric questions, ensure correct_answer is provided
            if (formData.type !== 'mcq' && !formData.correct_answer) {
                setError('Please provide the correct answer');
                setLoading(false);
                return;
            }
            
            const payload = {
                ...formData,
                // Filter out empty options
                options: formData.options.filter(opt => opt.text.trim() !== '')
            };
            
            let response;
            if (mode === 'edit') {
                response = await questionApi.updateQuestion(questionId, payload);
            } else {
                response = await questionApi.createQuestion(payload);
            }
            
            if (response.success) {
                navigate('/admin/question-bank');
            } else {
                setError(response.message || 'Failed to save question');
            }
        } catch (err) {
            console.error('Error saving question:', err);
            setError('An error occurred while saving the question');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading question...</span>
            </div>
        );
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                    {isViewMode ? 'View Question' : questionId ? 'Edit Question' : 'Create New Question'}
                </h1>
                {!isViewMode && (
                    <button
                        type="button"
                        onClick={() => navigate('/admin/question-bank')}
                        className="px-4 py-2 bg-zinc-200 dark:bg-zinc-700 text-zinc-800 dark:text-zinc-200 rounded-lg hover:bg-zinc-300 dark:hover:bg-zinc-600"
                    >
                        Cancel
                    </button>
                )}
            </div>

            {error && (
                <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded relative mb-6" role="alert">
                    <strong className="font-bold">Error!</strong>
                    <span className="block sm:inline"> {error}</span>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="glass-card p-6">
                    <div className="grid grid-cols-1 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Title
                            </label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleChange}
                                className="input-field"
                                required
                                disabled={isViewMode}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Question Text
                            </label>
                            <textarea
                                name="content"
                                value={formData.content}
                                onChange={handleChange}
                                rows={4}
                                className="input-field"
                                required
                                disabled={isViewMode}
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Question Type
                                </label>
                                <select
                                    name="type"
                                    value={formData.type}
                                    onChange={handleChange}
                                    className="input-field"
                                    disabled={isViewMode || mode === 'edit'} // Can't change type in edit mode
                                >
                                    <option value="mcq">Multiple Choice</option>
                                    <option value="msq">Multiple Select</option>
                                    <option value="text">Text Answer</option>
                                    <option value="numeric">Numeric Answer</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Difficulty
                                </label>
                                <select
                                    name="difficulty"
                                    value={formData.difficulty}
                                    onChange={handleChange}
                                    className="input-field"
                                    disabled={isViewMode}
                                >
                                    <option value="easy">Easy</option>
                                    <option value="medium">Medium</option>
                                    <option value="hard">Hard</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Points
                                </label>
                                <input
                                    type="number"
                                    name="points"
                                    value={formData.points}
                                    onChange={handleChange}
                                    min="1"
                                    max="100"
                                    className="input-field"
                                    required
                                    disabled={isViewMode}
                                />
                            </div>
                        </div>

                        {(formData.type === 'mcq' || formData.type === 'msq') && (
                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                                    Options
                                </label>
                                <div className="space-y-3">
                                    {formData.options.map((option, index) => (
                                        <div key={index} className="flex items-center space-x-2">
                                            <input
                                                type={formData.type === 'mcq' ? 'radio' : 'checkbox'}
                                                name={`option-${index}-correct`}
                                                checked={option.is_correct}
                                                onChange={(e) => handleOptionChange(index, 'is_correct', e.target.checked)}
                                                className="h-4 w-4 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400"
                                                disabled={isViewMode}
                                            />
                                            <input
                                                type="text"
                                                value={option.text}
                                                onChange={(e) => handleOptionChange(index, 'text', e.target.value)}
                                                placeholder={`Option ${index + 1}`}
                                                className="input-field flex-1"
                                                required
                                                disabled={isViewMode}
                                            />
                                            {!isViewMode && (
                                                <button
                                                    type="button"
                                                    onClick={() => removeOption(index)}
                                                    className="p-2 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                                                    disabled={formData.options.length <= 2}
                                                >
                                                    <FaTrash />
                                                </button>
                                            )}
                                        </div>
                                    ))}
                                    {!isViewMode && (
                                        <button
                                            type="button"
                                            onClick={addOption}
                                            className="mt-2 flex items-center space-x-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                                        >
                                            <FaPlus />
                                            <span>Add Option</span>
                                        </button>
                                    )}
                                </div>
                            </div>
                        )}

                        {(formData.type === 'text' || formData.type === 'numeric') && (
                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Correct Answer
                                </label>
                                <input
                                    type={formData.type === 'numeric' ? 'number' : 'text'}
                                    name="correct_answer"
                                    value={formData.correct_answer}
                                    onChange={handleChange}
                                    className="input-field"
                                    required
                                    disabled={isViewMode}
                                />
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Explanation (Optional)
                            </label>
                            <textarea
                                name="explanation"
                                value={formData.explanation}
                                onChange={handleChange}
                                rows={3}
                                className="input-field"
                                placeholder="Explain the correct answer..."
                                disabled={isViewMode}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Course (Optional)
                            </label>
                            <select
                                name="course_id"
                                value={formData.course_id}
                                onChange={handleChange}
                                className="input-field"
                                disabled={isViewMode}
                            >
                                <option value="">Select a course</option>
                                {courses.map(course => (
                                    <option key={course.id} value={course.id}>
                                        {course.code} - {course.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {!isViewMode && (
                            <div>
                                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                    Status
                                </label>
                                <select
                                    name="status"
                                    value={formData.status}
                                    onChange={handleChange}
                                    className="input-field"
                                >
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
                                </select>
                            </div>
                        )}
                    </div>
                </div>

                {!isViewMode && (
                    <div className="flex justify-end">
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={loading}
                        >
                            {loading ? 'Saving...' : questionId ? 'Update Question' : 'Create Question'}
                        </button>
                    </div>
                )}
            </form>
        </div>
    );
};

export default QuestionForm;