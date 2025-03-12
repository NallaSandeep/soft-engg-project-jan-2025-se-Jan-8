import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assignmentApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';
import { toast } from 'react-hot-toast';
import { formatDate } from '../../utils/dateUtils';
import { FaClock, FaCheckCircle, FaTimesCircle, FaInfoCircle } from 'react-icons/fa';
import { Card } from '../common/Card';

const safeJSONParse = (value) => {
    try {
        return typeof value === 'string' ? JSON.parse(value) : value;
    } catch (err) {
        // If it's a comma-separated string, convert it to an array
        if (typeof value === 'string' && value.includes(',')) {
            return value.split(',').map(item => item.trim());
        }
        return value;
    }
};

const AssignmentView = () => {
    const { courseId, assignmentId } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [assignment, setAssignment] = useState(null);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastSubmission, setLastSubmission] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchAssignment();
        fetchLastSubmission();
    }, [assignmentId]);

    const fetchAssignment = async () => {
        try {
            setLoading(true);
            const response = await assignmentApi.getAssignment(assignmentId);
            if (response.success) {
                setAssignment(response.data);
                // Initialize answers object
                const initialAnswers = {};
                response.data.questions.forEach(q => {
                    initialAnswers[q.id] = q.type === 'MSQ' ? [] : '';
                });
                setAnswers(initialAnswers);
            } else {
                setError(response.message || 'Failed to load assignment');
            }
        } catch (err) {
            console.error('Error loading assignment:', err);
            setError(err.message || 'Failed to load assignment');
        } finally {
            setLoading(false);
        }
    };

    const fetchLastSubmission = async () => {
        try {
            const response = await assignmentApi.getSubmissions(assignmentId);
            if (response.success && response.data.length > 0) {
                // Get the most recent submission
                const lastSub = response.data[0]; // Already sorted by submitted_at desc
                setLastSubmission(lastSub);
                console.log('Last submission:', lastSub); // Debug log
            }
        } catch (err) {
            console.error('Error fetching last submission:', err);
        }
    };

    const handleAnswerChange = (questionId, value) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: value
        }));
    };
    const [errorMessage, setErrorMessage] = useState(null);

    const handleSubmit = async () => {
        try {
            setSubmitting(true);
            setErrorMessage(null); // Clear previous errors

            const response = await assignmentApi.submitAssignment(assignmentId, { answers });

            if (response.success) {
                const scoreMessage = `Score: ${response.data.score}/${response.data.max_score}`;
                toast.success(
                    <div>
                        <div>Assignment submitted successfully!</div>
                        <div className="text-sm">{scoreMessage}</div>
                        {assignment.type === 'practice' && 
                            <div className="text-sm">You can try again to improve your score.</div>
                        }
                    </div>
                );

                await fetchLastSubmission();

                if (assignment.type === 'practice') {
                    const initialAnswers = {};
                    assignment.questions.forEach(q => {
                        initialAnswers[q.id] = q.type === 'MSQ' ? [] : '';
                    });
                    setAnswers(initialAnswers);
                } 
            } else {
                setErrorMessage(response.message || 'Failed to submit assignment'); // Display error on the page
            }
        } catch (err) {
            console.error('Error submitting assignment:', err);
            setErrorMessage(err.message || 'Failed to submit assignment'); // Store error
        } finally {
            setSubmitting(false);
        }
    };
    {errorMessage && (
        <div className="mt-4 p-3 text-red-600 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
            {errorMessage}
        </div>
    )}


    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading assignment...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-600 dark:text-red-400 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                {error}
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-6">
            {/* Assignment Header */}
            <Card className="p-6 mb-6 dark:bg-zinc-800">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">{assignment.title}</h1>
                <div className="text-zinc-600 dark:text-zinc-400 mb-4">{assignment.description}</div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span className="font-medium text-zinc-800 dark:text-zinc-300">Type: </span>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                            assignment.type === 'practice' 
                                ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400' 
                                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
                        }`}>
                            {assignment.type.charAt(0).toUpperCase() + assignment.type.slice(1)}
                        </span>
                    </div>
                    <div className="text-zinc-800 dark:text-zinc-300">
                        <span className="font-medium">Due Date: </span>
                        {assignment.due_date ? new Date(assignment.due_date).toLocaleString() : 'No due date'}
                    </div>
                    <div className="text-zinc-800 dark:text-zinc-300">
                        <span className="font-medium">Total Points: </span>
                        {assignment.points_possible}
                    </div>
                </div>

                {/* Submission History - More prominent placement */}
                {lastSubmission && (
                    <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800/50 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-300">Last Submission</h3>
                            <div className="text-sm text-blue-600 dark:text-blue-400">
                                {new Date(lastSubmission.submitted_at).toLocaleString()}
                            </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-white dark:bg-zinc-800 p-3 rounded-lg">
                                <div className="text-sm text-zinc-600 dark:text-zinc-400">Total Score</div>
                                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                    {lastSubmission.score}/{assignment.points_possible}
                                </div>
                            </div>
                            
                            {/* Question Scores */}
                            <div className="bg-white dark:bg-zinc-800 p-3 rounded-lg">
                                <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">Question Scores</div>
                                <div className="space-y-1">
                                    {Object.entries(lastSubmission.question_scores || {}).map(([questionId, score], index) => {
                                        const question = assignment.questions.find(q => q.id.toString() === questionId);
                                        return question ? (
                                            <div key={questionId} className="flex justify-between text-sm">
                                                <span className="text-zinc-800 dark:text-zinc-300">Q{index + 1}:</span>
                                                <span className={score > 0 
                                                    ? 'text-green-600 dark:text-green-400 font-semibold' 
                                                    : 'text-red-600 dark:text-red-400 font-semibold'
                                                }>
                                                    {score}/{question.points}
                                                </span>
                                            </div>
                                        ) : null;
                                    })}
                                </div>
                            </div>
                        </div>

                        {lastSubmission.status === 'late' && (
                            <div className="mt-2 text-yellow-600 dark:text-yellow-400 text-sm">
                                ⚠️ This submission was late
                            </div>
                        )}
                        
                        {assignment.type === 'practice' && (
                            <div className="mt-2 text-blue-600 dark:text-blue-400 text-sm flex items-center">
                                <span className="mr-1">ℹ️</span>
                                This is a practice assignment. You can submit again to improve your score.
                            </div>
                        )}
                    </div>
                )}
            </Card>

            {/* Questions */}
            <div className="space-y-6 mb-8">
                {assignment.questions.map((question, index) => (
                    <Card key={question.id} className="p-6 dark:bg-zinc-800">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-medium text-zinc-900 dark:text-white">
                                Question {index + 1}: {question.title}
                                <span className="ml-2 text-sm text-zinc-500 dark:text-zinc-400">({question.points} points)</span>
                            </h3>
                        </div>
                        <p className="text-zinc-700 dark:text-zinc-300 mb-4">{question.content}</p>

                        {/* Question type specific input */}
                        {question.type === 'MCQ' && (
                            <div className="space-y-2">
                                {question.options.map((option, optionIndex) => (
                                    <label key={optionIndex} className="flex items-center space-x-3 p-2 rounded hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200 transition-colors">
                                        <input
                                            type="radio"
                                            name={`question-${question.id}`}
                                            value={optionIndex}
                                            checked={answers[question.id] === optionIndex}
                                            onChange={(e) => handleAnswerChange(question.id, parseInt(e.target.value))}
                                            className="text-blue-600 dark:text-blue-500"
                                        />
                                        <span>{option}</span>
                                    </label>
                                ))}
                            </div>
                        )}

                        {question.type === 'MSQ' && (
                            <div className="space-y-2">
                                {question.options.map((option, optionIndex) => (
                                    <label key={optionIndex} className="flex items-center space-x-3 p-2 rounded hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200 transition-colors">
                                        <input
                                            type="checkbox"
                                            value={optionIndex}
                                            checked={answers[question.id].includes(optionIndex)}
                                            onChange={(e) => {
                                                const value = parseInt(e.target.value);
                                                handleAnswerChange(
                                                    question.id,
                                                    e.target.checked
                                                        ? [...answers[question.id], value]
                                                        : answers[question.id].filter(v => v !== value)
                                                );
                                            }}
                                            className="text-blue-600 dark:text-blue-500"
                                        />
                                        <span>{option}</span>
                                    </label>
                                ))}
                            </div>
                        )}

                        {question.type === 'NUMERIC' && (
                            <div>
                                <input
                                    type="number"
                                    value={answers[question.id]}
                                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                    className="w-full max-w-xs rounded-lg border-zinc-300 dark:border-zinc-600 shadow-sm bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                                    step="any"
                                    placeholder="Enter your answer..."
                                />
                            </div>
                        )}
                    </Card>
                ))}
            </div>

            {/* Submit Button - Fixed at bottom */}
            <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-zinc-800 border-t border-zinc-200 dark:border-zinc-700 p-4 shadow-md">
                <div className="max-w-4xl mx-auto flex justify-between items-center">
                    <div className="text-sm text-zinc-600 dark:text-zinc-400">
                        {assignment.type === 'practice' && 
                            "This is a practice assignment. You can submit multiple times."
                        }
                    </div>
                    <button
                        onClick={handleSubmit}
                        disabled={submitting}
                        className={`px-6 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors
                            ${submitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        {submitting ? 'Submitting...' : 'Submit Assignment'}
                    </button>
                    {errorMessage && (
                        <div className="mt-4 p-3 text-red-600 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
                            {errorMessage}
                        </div>
                    )}
                </div>
            </div>

            {/* Add padding at bottom to account for fixed submit button */}
            <div className="h-20"></div>
        </div>
    );
};

export default AssignmentView; 