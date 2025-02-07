import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi, questionBankApi, assignmentApi } from '../../../services/apiService';

const AssignmentForm = () => {
    const { courseId, weekId } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [selectedQuestions, setSelectedQuestions] = useState([]);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        type: 'practice',
        start_date: '',
        due_date: '',
        is_published: false
    });

    useEffect(() => {
        fetchQuestions();
    }, [courseId]);

    const fetchQuestions = async () => {
        try {
            setLoading(true);
            const response = await questionBankApi.getQuestions({
                status: 'active',
                course_id: courseId
            });
            setQuestions(response.data || []);
        } catch (err) {
            console.error('Error fetching questions:', err);
            setError('Failed to load questions');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleQuestionToggle = (questionId) => {
        setSelectedQuestions(prev => {
            if (prev.includes(questionId)) {
                return prev.filter(id => id !== questionId);
            } else {
                return [...prev, questionId];
            }
        });
    };

    const calculateTotalPoints = () => {
        return selectedQuestions.reduce((total, questionId) => {
            const question = questions.find(q => q.id === questionId);
            return total + (question?.points || 0);
        }, 0);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (selectedQuestions.length === 0) {
            setError('Please select at least one question');
            return;
        }

        try {
            // Create assignment
            const assignmentData = {
                ...formData,
                week_id: weekId,
                total_points: calculateTotalPoints()
            };
            const response = await assignmentApi.createAssignment(weekId, assignmentData);
            
            // Add questions to assignment
            await assignmentApi.addQuestions(response.data.id, selectedQuestions);
            
            navigate(`/admin/courses/${courseId}/content`);
        } catch (err) {
            console.error('Error creating assignment:', err);
            setError(err.message || 'Failed to create assignment');
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
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <button
                        onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                        className="hover:text-blue-600"
                    >
                        Course Content
                    </button>
                    <span>→</span>
                    <span>New Assignment</span>
                </div>
                <h1 className="text-2xl font-bold text-gray-900">Create New Assignment</h1>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 mb-6">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Info */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="grid grid-cols-1 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Title
                            </label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleInputChange}
                                className="w-full rounded-lg border-gray-300"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Description
                            </label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleInputChange}
                                className="w-full rounded-lg border-gray-300"
                                rows="3"
                                required
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Type
                                </label>
                                <select
                                    name="type"
                                    value={formData.type}
                                    onChange={handleInputChange}
                                    className="w-full rounded-lg border-gray-300"
                                    required
                                >
                                    <option value="practice">Practice</option>
                                    <option value="graded">Graded</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Start Date
                                </label>
                                <input
                                    type="datetime-local"
                                    name="start_date"
                                    value={formData.start_date}
                                    onChange={handleInputChange}
                                    className="w-full rounded-lg border-gray-300"
                                    required={formData.type === 'graded'}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Due Date
                                </label>
                                <input
                                    type="datetime-local"
                                    name="due_date"
                                    value={formData.due_date}
                                    onChange={handleInputChange}
                                    className="w-full rounded-lg border-gray-300"
                                    required={formData.type === 'graded'}
                                />
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                name="is_published"
                                checked={formData.is_published}
                                onChange={handleInputChange}
                                className="rounded border-gray-300 text-blue-600"
                            />
                            <label className="text-sm text-gray-700">
                                Publish immediately
                            </label>
                        </div>
                    </div>
                </div>

                {/* Question Selection */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold text-gray-900">
                            Select Questions
                        </h2>
                        <div className="text-sm text-gray-600">
                            Total Points: {calculateTotalPoints()}
                        </div>
                    </div>

                    <div className="space-y-4">
                        {questions.map(question => (
                            <div
                                key={question.id}
                                className={`p-4 rounded-lg border ${
                                    selectedQuestions.includes(question.id)
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200 hover:border-blue-300'
                                } transition-colors cursor-pointer`}
                                onClick={() => handleQuestionToggle(question.id)}
                            >
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="font-medium text-gray-900">
                                            {question.title}
                                        </h3>
                                        <p className="text-sm text-gray-600">
                                            {question.type} • {question.points} points
                                        </p>
                                    </div>
                                    <input
                                        type="checkbox"
                                        checked={selectedQuestions.includes(question.id)}
                                        onChange={() => {}}
                                        className="rounded border-gray-300 text-blue-600"
                                    />
                                </div>

                                <p className="text-gray-700 mt-2">{question.content}</p>

                                {/* Question Preview */}
                                <div className="mt-4 pl-4 border-l-2 border-gray-200">
                                    {question.type === 'MCQ' && question.options && (
                                        <div className="space-y-2">
                                            {question.options.map((option, index) => (
                                                <div key={index} className="flex items-center gap-2">
                                                    <input
                                                        type="radio"
                                                        disabled
                                                        className="text-blue-600"
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
                                                        className="text-blue-600"
                                                    />
                                                    <span>{option}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {question.type === 'Numeric' && (
                                        <div className="flex items-center gap-2">
                                            <input
                                                type="number"
                                                disabled
                                                placeholder="Enter numeric value"
                                                className="rounded-lg border-gray-300"
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}

                        {questions.length === 0 && (
                            <div className="text-center py-8 text-gray-600">
                                No active questions available for this course.
                                <br />
                                <button
                                    type="button"
                                    onClick={() => navigate('/admin/question-bank/new')}
                                    className="text-blue-600 hover:text-blue-800 mt-2"
                                >
                                    Create questions in the Question Bank
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex justify-end gap-4">
                    <button
                        type="button"
                        onClick={() => navigate(`/admin/courses/${courseId}/content`)}
                        className="px-4 py-2 text-gray-700 hover:text-gray-900"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Create Assignment
                    </button>
                </div>
            </form>
        </div>
    );
};

export default AssignmentForm; 