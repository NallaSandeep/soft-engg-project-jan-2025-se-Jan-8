import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { assignmentApi, questionBankApi } from '../../../services/apiService';
import {  
    TrashIcon, 
    PlusCircleIcon,
} from '@heroicons/react/24/outline';

const AssignmentView = () => {
    const { assignmentId } = useParams();
    const navigate = useNavigate();
    const [assignment, setAssignment] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [availableQuestions, setAvailableQuestions] = useState([]);
    const [selectedQuestions, setSelectedQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        type: '',
        difficulty: '',
        search: ''
    });
    const [showQuestionSelector, setShowQuestionSelector] = useState(false);

    useEffect(() => {
        fetchAssignment();
    }, [assignmentId]);

    const fetchAssignment = async () => {
        try {
            setLoading(true);
            const response = await assignmentApi.getAssignment(assignmentId);
            if (response.success) {
                setAssignment(response.data);
                setQuestions(response.data.questions || []);
            } else {
                setError('Failed to load assignment');
            }
        } catch (err) {
            console.error('Error loading assignment:', err);
            setError('Failed to load assignment');
        } finally {
            setLoading(false);
        }
    };

    const fetchAvailableQuestions = async () => {
        try {
            const response = await questionBankApi.getQuestions(filters);
            if (response.success) {
                // Filter out questions that are already in the assignment
                const existingQuestionIds = questions.map(q => q.id);
                setAvailableQuestions(
                    response.data.filter(q => !existingQuestionIds.includes(q.id))
                );
            }
        } catch (err) {
            console.error('Error loading questions:', err);
        }
    };

    useEffect(() => {
        if (showQuestionSelector) {
            fetchAvailableQuestions();
        }
    }, [showQuestionSelector, filters]);

    const handleFilterChange = (name, value) => {
        setFilters(prev => ({ ...prev, [name]: value }));
    };

    const handleQuestionSelect = (questionId) => {
        setSelectedQuestions(prev => {
            if (prev.includes(questionId)) {
                return prev.filter(id => id !== questionId);
            } else {
                return [...prev, questionId];
            }
        });
    };

    const handleAddSelectedQuestions = async () => {
        if (selectedQuestions.length === 0) return;
        
        try {
            const response = await assignmentApi.addQuestions(assignmentId, selectedQuestions);
            if (response.success) {
                fetchAssignment();
                setShowQuestionSelector(false);
                setSelectedQuestions([]);
            }
        } catch (err) {
            console.error('Error adding questions:', err);
        }
    };

    const handleRemoveQuestion = async (questionId) => {
        if (!window.confirm('Are you sure you want to remove this question?')) return;
        
        try {
            await assignmentApi.removeQuestion(assignmentId, questionId);
            fetchAssignment();
        } catch (err) {
            console.error('Error removing question:', err);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading assignment...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2 dark:text-gray-400">
                    <button
                        onClick={() => navigate('/admin/assignments')}
                        className="hover:text-blue-600 dark:hover:text-blue-400"
                    >
                        Assignments
                    </button>
                    <span>→</span>
                    <span>View Assignment</span>
                </div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {assignment?.title}
                </h1>
            </div>

            {/* Assignment Details */}
            <div className="bg-gray-100 rounded-lg shadow p-6 mb-6 dark:bg-zinc-800">
                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <h2 className="text-lg font-semibold mb-4">Details</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-400">Title</label>
                                <input
                                    type="text"
                                    value={assignment?.title || ''}
                                    readOnly
                                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 bg-gray-50 dark:bg-zinc-800 dark:border-zinc-700"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-400">Description</label>
                                <textarea
                                    value={assignment?.description || ''}
                                    readOnly
                                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 bg-gray-50 dark:bg-zinc-800 dark:border-zinc-700"
                                    rows="3"
                                />
                            </div>
                        </div>
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold mb-4">Settings</h2>
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-400">Type</label>
                                    <input
                                        type="text"
                                        value={assignment?.type || ''}
                                        readOnly
                                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 bg-gray-50 dark:bg-zinc-800 dark:border-zinc-700"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-400">Points</label>
                                    <input
                                        type="text"
                                        value={assignment?.points_possible || '0'}
                                        readOnly
                                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 bg-gray-50 dark:bg-zinc-800 dark:border-zinc-700"
                                    />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-400">Start Date</label>
                                    <input
                                        type="text"
                                        value={assignment.start_date ? new Date(assignment.start_date)
                                            .toISOString()
                                            .slice(0,16)
                                            .replace('T',' ')
                                        : ''}
                                        readOnly
                                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 bg-gray-50 dark:bg-zinc-800 dark:border-zinc-700"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-400">Due Date</label>
                                    <input
                                        type="text"
                                        value={assignment.due_date ? new Date(assignment.due_date)
                                            .toISOString()
                                            .slice(0,16)
                                            .replace('T',' ')
                                        : ''}
                                        readOnly
                                        className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 bg-gray-50 dark:bg-zinc-800 dark:border-zinc-700"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Questions Section */}
            <div className="bg-gray-50 rounded-lg shadow dark:bg-zinc-800">
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex justify-between items-center">
                        <h2 className="text-lg font-semibold">Questions</h2>
                        <button
                            onClick={() => setShowQuestionSelector(true)}
                            className="flex text-sm items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                        >
                            <PlusCircleIcon className="h-5 w-5" /> Add Questions
                        </button>
                    </div>
                </div>

                {/* Question List */}
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                    {questions.map((question, index) => (
                        <div key={question.id} className="p-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="font-medium text-sm text-gray-900 dark:text-zinc-300">
                                        Question {index + 1}: {question.title}
                                    </h3>
                                    <p className="text-xs text-blue-600 mt-1 dark:text-blue-300">
                                        {question.type} • {question.points} points
                                    </p>
                                </div>
                                <button
                                    onClick={() => handleRemoveQuestion(question.id)}
                                    className="text-red-600 hover:text-red-800 dark:text-red-200 dark:hover:text-red-400"
                                    title="Remove Question"
                                >
                                   <TrashIcon className="h-5 w-5" />
                                </button>
                            </div>
                            <div className="mt-4">
                                <p className="text-gray-700 dark:text-zinc-100">{question.content}</p>
                                {question.type === 'MCQ' && question.options && (
                                    <div className="mt-4 space-y-2">
                                        {question.options.map((option, optionIndex) => (
                                            <div key={optionIndex} className="flex items-center gap-2 text-sm">
                                                <input
                                                    type="radio"
                                                    disabled
                                                    className="text-blue-600 dark:bg-zinc-700 dark:border-zinc-400"
                                                />
                                                <span>{option}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                {question.type === 'MSQ' && question.options && (
                                    <div className="mt-4 space-y-2">
                                        {question.options.map((option, optionIndex) => (
                                            <div key={optionIndex} className="flex items-center gap-2 text-sm">
                                                <input
                                                    type="radio"
                                                    disabled
                                                    className="text-blue-600 dark:bg-zinc-700 dark:border-zinc-400 rounded"
                                                />
                                                <span>{option}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {questions.length === 0 && (
                        <div className="p-6 text-center text-gray-500">
                            No questions added to this assignment yet.
                        </div>
                    )}
                </div>
            </div>

            {/* Question Selector Modal */}
            {showQuestionSelector && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden dark:bg-zinc-800">
                        <div className="p-6 border-b border-gray-200 dark:border-zinc-700">
                            <div className="flex justify-between items-center">
                                <h2 className="text-lg font-semibold">Add Questions</h2>
                                <button
                                    onClick={() => {
                                        setShowQuestionSelector(false);
                                        setSelectedQuestions([]);
                                    }}
                                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                                >
                                    ×
                                </button>
                            </div>
                        </div>

                        {/* Filters */}
                        <div className="p-6 border-b border-gray-200 dark:border-zinc-700">
                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                                        Type
                                    </label>
                                    <select
                                        value={filters.type}
                                        onChange={(e) => handleFilterChange('type', e.target.value)}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 dark:bg-zinc-700 dark:border-zinc-700"
                                    >
                                        <option value="">All Types</option>
                                        <option value="MCQ">Multiple Choice</option>
                                        <option value="MSQ">Multiple Select</option>
                                        <option value="Numeric">Numeric</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                                        Difficulty
                                    </label>
                                    <select
                                        value={filters.difficulty}
                                        onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 dark:bg-zinc-700 dark:border-zinc-700"
                                    >
                                        <option value="">All Difficulties</option>
                                        <option value="easy">Easy</option>
                                        <option value="medium">Medium</option>
                                        <option value="hard">Hard</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                                        Search
                                    </label>
                                    <input
                                        type="text"
                                        value={filters.search}
                                        onChange={(e) => handleFilterChange('search', e.target.value)}
                                        placeholder="Search questions..."
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 dark:bg-zinc-700 dark:border-zinc-700"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Available Questions */}
                        <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 300px)' }}>
                            <div className="space-y-4">
                                {availableQuestions.map(question => (
                                    <div
                                        key={question.id}
                                        className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                                            selectedQuestions.includes(question.id)
                                                ? 'border-blue-500 bg-blue-50 dark:bg-zinc-900 dark:border-blue-400'
                                                : 'border-gray-200 hover:border-blue-500 dark:border-zinc-600 dark:hover:border-blue-400'
                                        }`}
                                        onClick={() => handleQuestionSelect(question.id)}
                                    >
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="font-medium text-gray-900 dark:text-zinc-400 text-xs">
                                                    {question.title}
                                                </h3>
                                                <p className="text-xs text-blue-600 dark:text-blue-300 mt-1">
                                                    {question.type} • {question.points} points • {question.difficulty || 'No difficulty set'}
                                                </p>
                                            </div>
                                            <input
                                                type="checkbox"
                                                checked={selectedQuestions.includes(question.id)}
                                                onChange={() => handleQuestionSelect(question.id)}
                                                onClick={(e) => e.stopPropagation()}
                                                className="h-5 w-5 text-blue-600 rounded border-gray-300 dark:bg-zinc-700 dark:border-zinc-400 "
                                            />
                                        </div>
                                        <p className="text-zinc-700 mt-2 dark:text-zinc-100">{question.content}</p>
                                    </div>
                                ))}

                                {availableQuestions.length === 0 && (
                                    <div className="text-center text-gray-500">
                                        No available questions found.
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Footer with Add Selected Button */}
                        <div className="p-4 border-t border-gray-200 bg-gray-50 dark:bg-zinc-700 dark:border-zinc-500">
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-300">
                                    {selectedQuestions.length} questions selected
                                </span>
                                <button
                                    onClick={handleAddSelectedQuestions}
                                    disabled={selectedQuestions.length === 0}
                                    className={`px-4 py-2 rounded-lg ${
                                        selectedQuestions.length === 0
                                            ? 'bg-zinc-200 dark:bg-zinc-600 cursor-not-allowed text-gray-400'
                                            : 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer dark:bg-blue-700 dark:hover:bg-blue-800 dark:text-white'
                                    }`}
                                >
                                    Add Selected Questions
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AssignmentView; 