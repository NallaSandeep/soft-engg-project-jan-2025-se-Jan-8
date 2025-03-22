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
        options: ['', ''],  // Start with 2 empty options
        correct_answer: '',
        points: 1,
        explanation: '',
        course_id: '',
        week_id: '',
        lecture_id: '',
        status: 'draft'
    });

    const isViewMode = mode === 'view';

    useEffect(() => {
        fetchCourses();
        if (questionId) {
            fetchQuestion();
        } else {
            setLoading(false);
        }
    }, [questionId]);

    const fetchCourses = async () => {
        try {
            const response = await courseApi.getCourses();
            if (response.success) {
                setCourses(response.data || []);
            } else {
                console.error('Failed to load courses:', response.message);
            }
        } catch (err) {
            console.error('Error fetching courses:', err);
            setError('Failed to load courses');
        }
    };

    const fetchQuestion = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await questionBankApi.getQuestion(questionId);
            if (response.success) {
                const question = response.data;
                setFormData({
                    title: question.title || '',
                    content: question.content || '',
                    type: question.type || 'MCQ',
                    options: Array.isArray(question.options) ? question.options : ['', ''],
                    correct_answer: question.correct_answer ?? (question.type === 'MSQ' ? [] : ''),
                    points: question.points || 1,
                    explanation: question.explanation || '',
                    course_id: question.course_id || '',
                    week_id: question.week_id || '',
                    lecture_id: question.lecture_id || '',
                    status: question.status || 'draft'
                });
            } else {
                setError(response.message || 'Failed to load question');
            }
        } catch (err) {
            console.error('Error fetching question:', err);
            setError(err.message || 'Failed to load question');
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
    };

    const handleOptionChange = (index, value) => {
        const newOptions = [...formData.options];
        newOptions[index] = value;
        setFormData(prev => ({
            ...prev,
            options: newOptions
        }));
    };

    const addOption = () => {
        setFormData(prev => ({
            ...prev,
            options: [...prev.options, '']
        }));
    };

    const removeOption = (index) => {
        setFormData(prev => ({
            ...prev,
            options: prev.options.filter((_, i) => i !== index)
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = { ...formData };
            
            // Format data based on question type
            if (data.type === 'MCQ') {
                data.correct_answer = parseInt(data.correct_answer);
            } else if (data.type === 'MSQ') {
                data.correct_answer = Array.isArray(data.correct_answer) 
                    ? data.correct_answer.map(Number) 
                    : [];
            } else if (data.type === 'NUMERIC') {
                data.correct_answer = parseFloat(data.correct_answer);
                data.options = []; // No options for numeric questions
            }

            // Ensure points is a number
            data.points = parseInt(data.points);

            // Remove empty options and set as question_options
            if (data.type !== 'NUMERIC') {
                data.question_options = data.options.filter(opt => opt.trim() !== '');
            } else {
                data.question_options = [];
            }
            delete data.options;  // Remove the old options field

            const response = questionId 
                ? await questionBankApi.updateQuestion(questionId, data)
                : await questionBankApi.createQuestion(data);

            if (response.success) {
                navigate('/admin/question-bank');
            } else {
                setError(response.message || 'Failed to save question');
            }
        } catch (err) {
            console.error('Error saving question:', err);
            setError(err.message || 'Failed to save question');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading...</div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <button
                        onClick={() => navigate('/admin/question-bank')}
                        className="hover:text-blue-600 dark:hover:text-blue-400 dark:text-gray-400"
                    >
                        Question Bank
                    </button>
                    <span>→</span>
                    <span className='dark: text-gray-400'>{isViewMode ? 'View Question' : (questionId ? 'Edit Question' : 'New Question')}</span>
                </div>
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-200">
                        {isViewMode ? 'View Question' : (questionId ? 'Edit Question' : 'Create New Question')}
                    </h1>
                    {isViewMode && (
                        <button
                            onClick={() => navigate(`/admin/question-bank/${questionId}/edit`)}
                            className="bg-blue-600 text-gray-100 px-4 py-2 rounded-lg hover:bg-blue-700 dark"
                        >
                            Edit Question
                        </button>
                    )}
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 mb-6">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="bg-gray-50 dark:bg-zinc-800 rounded-lg shadow p-6">
                    {/* Basic Info */}
                    <div className="grid grid-cols-1 gap-6 mb-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-1">
                                Title
                            </label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleInputChange}
                                className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                required
                                disabled={isViewMode}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-1">
                                Question Text
                            </label>
                            <textarea
                                name="content"
                                value={formData.content}
                                onChange={handleInputChange}
                                className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                rows="3"
                                required
                                disabled={isViewMode}
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-1">
                                    Question Type
                                </label>
                                <select
                                    name="type"
                                    value={formData.type}
                                    onChange={handleInputChange}
                                    className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                    required
                                    disabled={isViewMode}
                                >
                                    <option value="MCQ">Multiple Choice</option>
                                    <option value="MSQ">Multiple Select</option>
                                    <option value="NUMERIC">Numeric</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-1">
                                    Points
                                </label>
                                <input
                                    type="number"
                                    name="points"
                                    value={formData.points}
                                    onChange={handleInputChange}
                                    className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                    min="1"
                                    required
                                    disabled={isViewMode}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Options and Answer */}
                    {(formData.type === 'MCQ' || formData.type === 'MSQ') && (
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-2">
                                Options
                            </label>
                            <div className="space-y-2">
                                {formData.options.map((option, index) => (
                                    <div key={index} className="flex gap-2">
                                        <input
                                            type="text"
                                            value={option}
                                            onChange={(e) => handleOptionChange(index, e.target.value)}
                                            className="flex-1 rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                            placeholder={`Option ${index + 1}`}
                                            required
                                            disabled={isViewMode}
                                        />
                                        {formData.options.length > 2 && (
                                            <button
                                                type="button"
                                                onClick={() => removeOption(index)}
                                                className="text-red-600 hover:text-red-800 dark:text-red-200 dark:hover:text-red-400"
                                                disabled={isViewMode}
                                            >
                                                Remove
                                            </button>
                                        )}
                                    </div>
                                ))}
                                <button
                                    type="button"
                                    onClick={addOption}
                                    className="text-blue-600 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-400"
                                    disabled={isViewMode}
                                >
                                    Add Option
                                </button>
                            </div>
                        </div>
                    )}

                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-1">
                            Correct Answer
                        </label>
                        {formData.type === 'MCQ' && (
                            <select
                                name="correct_answer"
                                value={formData.correct_answer}
                                onChange={handleInputChange}
                                className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                required
                                disabled={isViewMode}
                            >
                                <option value="">Select correct answer</option>
                                {formData.options.map((option, index) => (
                                    <option key={index} value={index}>
                                        {option}
                                    </option>
                                ))}
                            </select>
                        )}

                        {formData.type === 'MSQ' && (
                            <div className="space-y-2">
                                {formData.options.map((option, index) => (
                                    <label key={index} className="flex items-center gap-2">
                                        <input
                                            type="checkbox"
                                            checked={formData.correct_answer.includes(index)}
                                            onChange={(e) => {
                                                const newAnswer = e.target.checked
                                                    ? [...formData.correct_answer, index]
                                                    : formData.correct_answer.filter(i => i !== index);
                                                setFormData(prev => ({
                                                    ...prev,
                                                    correct_answer: newAnswer
                                                }));
                                            }}
                                            className="text-blue-600 dark:text-blue-400 dark:bg-zinc-600"
                                            disabled={isViewMode}
                                        />
                                        <span>{option}</span>
                                    </label>
                                ))}
                            </div>
                        )}

                        {formData.type === 'NUMERIC' && (
                            <input
                                type="number"
                                name="correct_answer"
                                value={formData.correct_answer}
                                onChange={handleInputChange}
                                className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                step="any"
                                required
                                disabled={isViewMode}
                            />
                        )}
                    </div>

                    {/* Organization */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-1">
                                Course
                            </label>
                            <select
                                name="course_id"
                                value={formData.course_id}
                                onChange={handleInputChange}
                                className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                required
                                disabled={isViewMode}
                            >
                                <option value="">Select Course</option>
                                {courses.map(course => (
                                    <option key={course.id} value={course.id}>
                                        {course.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-1">
                                Status
                            </label>
                            <select
                                name="status"
                                value={formData.status}
                                onChange={handleInputChange}
                                className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                                required
                                disabled={isViewMode}
                            >
                                <option value="draft">Draft</option>
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-zinc-400 mb-1">
                            Explanation
                        </label>
                        <textarea
                            name="explanation"
                            value={formData.explanation}
                            onChange={handleInputChange}
                            className="w-full rounded-lg border-gray-300 dark:bg-zinc-800 dark:text-gray-100 dark:border-zinc-500"
                            rows="3"
                            placeholder="Explain the correct answer (optional)"
                            disabled={isViewMode}
                        />
                    </div>
                </div>

                {!isViewMode && (
                    <div className="flex justify-end gap-4">
                        <button
                            type="button"
                            onClick={() => navigate('/admin/question-bank')}
                            className="px-4 py-2 text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                        >
                            {questionId ? 'Update Question' : 'Create Question'}
                        </button>
                    </div>
                )}
            </form>
        </div>
    );
};

export default QuestionForm; 