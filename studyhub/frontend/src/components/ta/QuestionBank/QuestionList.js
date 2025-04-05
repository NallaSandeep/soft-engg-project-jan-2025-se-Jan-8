import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { questionBankApi, courseApi } from '../../../services/apiService';

const QuestionList = () => {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        status: 'active',
        type: '',
        course_id: '',
        week_id: '',
        lecture_id: ''
    });
    const [courses, setCourses] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchQuestions();
        fetchCourses();
    }, [filters]);

    const fetchQuestions = async () => {
        try {
            setLoading(true);
            const response = await questionBankApi.getQuestions(filters);
            setQuestions(response.data || []);
        } catch (err) {
            console.error('Error fetching questions:', err);
            setError(err.message || 'Failed to load questions');
        } finally {
            setLoading(false);
        }
    };

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
        }
    };

    const handleFilterChange = (field, value) => {
        setFilters(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleRowClick = (questionId) => {
        navigate(`/ta/question-bank/${questionId}`);
    };

    const handleEdit = (e, questionId) => {
        e.stopPropagation(); // Prevent row click
        navigate(`/ta/question-bank/${questionId}/edit`);
    };

    const handleDelete = async (e, questionId) => {
        e.stopPropagation(); // Prevent row click
        if (!window.confirm('Are you sure you want to delete this question?')) return;
        
        try {
            const response = await questionBankApi.deleteQuestion(questionId);
            if (response.success) {
                fetchQuestions();
            } else {
                setError(response.message || 'Failed to delete question');
            }
        } catch (err) {
            console.error('Error deleting question:', err);
            setError(err.message || 'Failed to delete question');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading questions...</div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <div className="flex justify-between items-center mb-4">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Question Bank</h1>
                    <button
                        onClick={() => navigate('/ta/question-bank/new')}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
                    >
                        Add Question
                    </button>
                </div>

                {/* Filters */}
                <div className="bg-zinc-10 rounded-lg shadow p-4 mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-2">
                        <select
                            value={filters.status}
                            onChange={(e) => handleFilterChange('status', e.target.value)}
                             className="input-field"
                        >
                            <option value="">All Status</option>
                            <option value="draft">Draft</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>

                        <select
                            value={filters.type}
                            onChange={(e) => handleFilterChange('type', e.target.value)}
                             className="input-field"
                        >
                            <option value="">All Types</option>
                            <option value="MCQ">Multiple Choice</option>
                            <option value="MSQ">Multiple Select</option>
                            <option value="NUMERIC">Numeric</option>
                        </select>

                        <select
                            value={filters.course_id}
                            onChange={(e) => handleFilterChange('course_id', e.target.value)}
                             className="input-field"
                        >
                            <option value="">All Courses</option>
                            {courses.map(course => (
                                <option key={course.id} value={course.id}>
                                    {course.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 mb-6">
                    {error}
                </div>
            )}

            {/* Questions List */}
            <div className="space-y-4">
                {questions.map(question => (
                    <div
                        key={question.id}
                        className="bg-zinc-100 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer dark:bg-zinc-800"
                        onClick={() => handleRowClick(question.id)}
                    >
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-400">
                                        {question.title}
                                    </h3>
                                    <p className="text-sm text-blue-600 dark:text-blue-300">
                                        {question.type} • {question.points} points
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={`px-3 py-1 rounded-full text-sm ${
                                        question.status === 'active'
                                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                            : question.status === 'draft'
                                            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                                    }`}>
                                        {question.status.charAt(0).toUpperCase() + question.status.slice(1)}
                                    </span>
                                    <div className="flex gap-2 ml-4">
                                        <button
                                            onClick={(e) => handleEdit(e, question.id)}
                                            className="p-1 text-blue-600 hover:text-blue-800 rounded-full hover:bg-blue-50 dark:hover:bg-blue-900/20 dark:text-blue-400"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                        </button>
                                        <button
                                            onClick={(e) => handleDelete(e, question.id)}
                                            className="p-1 text-red-600 hover:text-red-800 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 dark:text-red-400"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <p className="text-gray-700 mb-2 dark:text-gray-100">{question.content}</p>

                            {/* Question Preview */}
                            <div className="bg-gray-100 text-sm rounded-lg p-2 dark:bg-zinc-800">
                                {question.type === 'MCQ' && question.options && (
                                    <div className="space-y-2">
                                        {question.options.map((option, index) => (
                                            <div key={index} className="flex items-center gap-2">
                                                <input
                                                    type="radio"
                                                    name={`question-${question.id}`}
                                                    disabled
                                                    className="bg-zinc-100 dark:bg-zinc-700 text-blue-600 dark:text-blue-400"
                                                />
                                                <span>{option}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {question.type === 'MSQ' && question.options && (
                                    <div className="space-y-2">
                                        {question.options.map((option, index) => (
                                            <div key={index} className="flex items-center gap-2">
                                                <input
                                                    type="checkbox"
                                                    disabled
                                                    className="bg-zinc-100 dark:bg-zinc-700 text-blue-600 dark:text-blue-400"
                                                />
                                                <span>{option}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {question.type === 'NUMERIC' && (
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="number"
                                            disabled
                                            placeholder="Enter numeric value"
                                            className="rounded-lg border-gray-300 dark:border-gray-500 bg-zinc-100 dark:bg-zinc-700"
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {questions.length === 0 && (
                    <div className="bg-white rounded-lg shadow p-8 text-center">
                        <p className="text-gray-600">No questions found.</p>
                        <p className="text-sm text-gray-500 mt-2">
                            Create your first question to get started.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default QuestionList; 