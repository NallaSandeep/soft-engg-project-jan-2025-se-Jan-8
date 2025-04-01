import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assignmentApi, courseApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';
import { toast } from 'react-hot-toast';
import { formatDate } from '../../utils/dateUtils';
import { FaClock, FaCheckCircle, FaTimesCircle, FaInfoCircle } from 'react-icons/fa';
import { Card } from '../common/Card';
import { CheckCircleIcon, ClockIcon, DocumentTextIcon, PlayIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/outline';

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
    const [course, setCourse] = useState(null);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastSubmission, setLastSubmission] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [courseProgress, setCourseProgress] = useState(null);
    const [showResults, setShowResults] = useState(false);
    const [correctAnswers, setCorrectAnswers] = useState(null);
    const [errorMessage, setErrorMessage] = useState(null);
    const [summary, setSummary] = useState(null);
    const [isSummarizing, setIsSummarizing] = useState(false);
    const [summaryError, setSummaryError] = useState(null);

    useEffect(() => {
        fetchAssignment();
        fetchLastSubmission();
        fetchCourseContent();
        fetchCourseProgress();
        setErrorMessage(null);
        setSummary(null);
    }, [assignmentId]);

    useEffect(() => {
        if (assignment && lastSubmission) {
            const now = new Date();
            const dueDate = new Date(assignment.due_date);
            const isPractice = assignment.type === 'practice';
            
            // Show results if:
            // 1. It's a practice assignment and has at least one submission
            // 2. It's a graded assignment and due date has passed
            const shouldShow = (isPractice && lastSubmission) || (!isPractice && now > dueDate);
            setShowResults(shouldShow);
            
            // If we should show results, fetch correct answers
            if (shouldShow) {
                fetchCorrectAnswers();
            }
        }
    }, [assignment, lastSubmission]);

    const fetchCourseContent = async () => {
        try {
            const response = await courseApi.getCourseContent(courseId);
            if (response.success) {
                setCourse(response.data);
            }
        } catch (err) {
            console.error('Error loading course content:', err);
        }
    };

    const fetchAssignment = async () => {
        try {
            setLoading(true);
            const response = await assignmentApi.getAssignment(assignmentId);
            if (response.success) {
                setAssignment(response.data);
                
                // Get last submission first
                const submissionResponse = await assignmentApi.getSubmissions(assignmentId);
                const lastSub = submissionResponse.success && submissionResponse.data.length > 0 
                    ? submissionResponse.data[0] 
                    : null;
                setLastSubmission(lastSub);

                // Initialize answers object with last submission data if available
                const initialAnswers = {};
                response.data.questions.forEach(q => {
                    if (lastSub && lastSub.answers[q.id]) {
                        initialAnswers[q.id] = lastSub.answers[q.id].answer;
                    } else {
                    initialAnswers[q.id] = q.type === 'MSQ' ? [] : '';
                    }
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

    const fetchCourseProgress = async () => {
        try {
            const response = await courseApi.getCourseProgress(courseId);
            if (response.success) {
                setCourseProgress(response.data);
            }
        } catch (err) {
            console.error('Error loading course progress:', err);
        }
    };

    const handleAnswerChange = (questionId, value) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: value
        }));
    };

    // Initialize answers with proper types
    useEffect(() => {
        if (assignment) {
            const initialAnswers = {};
            assignment.questions.forEach(q => {
                if (lastSubmission && lastSubmission.answers[q.id]) {
                    initialAnswers[q.id] = lastSubmission.answers[q.id].answer;
                } else {
                    // Initialize with proper types
                    initialAnswers[q.id] = q.type === 'MSQ' ? [] : '';
                }
            });
            setAnswers(initialAnswers);
        }
    }, [assignment, lastSubmission]);

    // Add new function to fetch correct answers
    const fetchCorrectAnswers = async () => {
        try {
            const response = await assignmentApi.getCorrectAnswers(assignmentId);
            if (response.success) {
                setCorrectAnswers(response.data.questions);
            }
        } catch (err) {
            console.error('Error fetching correct answers:', err);
            // Don't show error to user - this is expected when conditions aren't met
        }
    };

    const handleSubmit = async () => {
        try {
            setSubmitting(true);
            setErrorMessage(null); // Clear previous errors
            const response = await assignmentApi.submitAssignment(assignmentId, { 
                answers,
                user_id: user.id // Add user ID to submission data
            });
            
            if (response.success) {
                // Show score in toast message
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

                // Refresh last submission data
                await fetchLastSubmission();

                // For practice assignments, clear answers for next attempt
                if (assignment.type === 'practice') {
                    const initialAnswers = {};
                    assignment.questions.forEach(q => {
                        initialAnswers[q.id] = q.type === 'MSQ' ? [] : '';
                    });
                    setAnswers(initialAnswers);
                }
            } else {
                setErrorMessage(response.message || 'Failed to submit assignment');
            }
        } catch (err) {
            console.error('Error submitting assignment:', err);
            setErrorMessage(err.message || 'Failed to submit assignment');
            toast.error(err.message || 'Failed to submit assignment');
        } finally {
            setSubmitting(false);
        }
    };

    const canSubmit = () => {
        if (!assignment) return false;
        const now = new Date();
        const dueDate = new Date(assignment.due_date);
        
        // Can't submit after due date
        if (now > dueDate) return false;
        
        // Practice assignments can always be submitted before due date
        if (assignment.type === 'practice') return true;
        
        // Graded assignments can be submitted multiple times before due date
        return true;
    };

    const fetchSummary = async () => {
        setIsSummarizing(true);
        setSummaryError(null);
        
        try {
            const contentToSummarize = {
                courseDescription: course.description,
                weeks: course.weeks?.map(week => ({
                    title: week.title,
                    description: week.description,
                    lectures: week.lectures?.map(lecture => lecture.title + ": " + lecture.description),
                    assignments: week.assignments?.map(assignment => assignment.title + (assignment.description ? ": " + assignment.description : ""))
                }))
            };
    
            const response = await fetch('http://127.0.0.1:5010/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: `Please provide suggestions for this assignment submission. 
                     here is the assignement ${JSON.stringify(assignment)}.
                     Here are submitted answers ${JSON.stringify(answers)}. 
                     Here is the correct answers ${JSON.stringify(correctAnswers)}
                     Show just summary. No bullet points.`,
                })
            });
    
            if (!response.ok) throw new Error('Failed to fetch summary');
            const data = await response.json();
            setSummary(data.content|| data.response || "No summary available");
        } catch (err) {
            console.error('Error fetching summary:', err);
            setSummaryError('Failed to generate summary');
        } finally {
            setIsSummarizing(false);
        }
    };

    // Update the submission details display
    const renderSubmissionDetails = () => {
        if (!lastSubmission) {
            return (
                <div className="mt-4 p-4 rounded-lg bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700">
                    <div className="text-zinc-600 dark:text-zinc-400">
                        No submissions yet
                    </div>
                </div>
            );
        }
        
        // Determine submission status text and color
        let statusText;
        let statusColor;
        
        if (lastSubmission.status === 'late') {
            statusText = 'Submitted Late';
            statusColor = 'text-yellow-600 dark:text-yellow-400';
        } else if (lastSubmission.status === 'graded') {
            statusText = 'Graded';
            statusColor = 'text-blue-600 dark:text-blue-400';
        } else {
            statusText = 'Submitted On Time';
            statusColor = 'text-green-600 dark:text-green-400';
        }
        
        return (
            <div className="mt-4 p-4 rounded-lg bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700">
                <h3 className="text-lg font-medium text-zinc-900 dark:text-white mb-2">
                    Last Submission Details
                </h3>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <span className="font-medium">Submitted:</span>{' '}
                        {new Date(lastSubmission.submitted_at).toLocaleString()}
                    </div>
                    <div>
                        <span className="font-medium">Status:</span>{' '}
                        <span className={statusColor}>
                            {statusText}
                        </span>
                    </div>
                    {(showResults || assignment.type === 'practice') && (
                        <div>
                            <span className="font-medium">Score:</span>{' '}
                            <span className="text-blue-600 dark:text-blue-400">
                                {lastSubmission.score}/{assignment.points_possible}
                            </span>
                        </div>
                    )}
                </div>
            </div>
        );
    };

    // Update the formatCorrectAnswer function to use correctAnswers data
    const formatCorrectAnswer = (questionId) => {
        const question = correctAnswers?.find(q => q.id === questionId);
        if (!question) return '';
        
        try {
            switch (question.type) {
                case 'MCQ':
                    return question.options[question.correct_answer] || 'Invalid answer';
                    
                case 'MSQ':
                    if (!Array.isArray(question.correct_answer) || !Array.isArray(question.options)) {
                        return 'Invalid answer format';
                    }
                    return question.correct_answer
                        .map(index => question.options[index])
                        .join(', ') || 'No correct answers specified';
                    
                case 'NUMERIC':
                    return question.correct_answer?.toString() || 'Invalid answer';
                    
                default:
                    return 'Unknown question type';
            }
        } catch (error) {
            console.error('Error formatting answer:', error);
            return 'Error displaying answer';
        }
    };

    // Update the renderQuestion function to use correctAnswers
    const renderQuestion = (question, index) => {
        if (!question) return null;
        
        const lastAnswer = lastSubmission?.answers[question.id];
        const questionScore = lastSubmission?.question_scores?.[question.id] || 0;
        const shouldShowResults = showResults || assignment.type === 'practice';
        const showCorrectAnswer = correctAnswers !== null;
        const correctAnswer = correctAnswers?.find(q => q.id === question.id);
        
        // Ensure answers[question.id] is properly initialized
        const currentAnswer = answers[question.id] ?? (question.type === 'MSQ' ? [] : '');
        
        return (
            <Card key={question.id} className="p-6 dark:bg-zinc-800">
                <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-medium text-zinc-900 dark:text-white">
                        Question {index + 1}: {question.title}
                        <span className="ml-2 text-sm text-zinc-500 dark:text-zinc-400">
                            ({question.points} points)
                        </span>
                    </h3>
                    {shouldShowResults && lastSubmission && (
                        <div className={`text-sm font-medium ${
                            questionScore === question.points
                                ? 'text-green-600 dark:text-green-400' 
                                : 'text-red-600 dark:text-red-400'
                        }`}>
                            Score: {questionScore}/{question.points}
                        </div>
                    )}
                </div>
                
                <p className="text-zinc-700 dark:text-zinc-300 mb-4">{question.content}</p>
                
                {/* Question type specific input */}
                {question.type === 'MCQ' && (
                    <div className="space-y-2">
                        {question.options.map((option, optionIndex) => {
                            const isSelected = answers[question.id] === optionIndex;
                            const wasSelected = lastAnswer?.answer === optionIndex;
                            let optionClass = "flex items-center space-x-3 p-2 rounded transition-colors ";
                            
                            if (shouldShowResults && lastSubmission && wasSelected) {
                                optionClass += lastAnswer?.is_correct
                                    ? "bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-400 " 
                                    : "bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-400 ";
                            } else {
                                optionClass += "hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200 ";
                            }
                            
                            return (
                            <label key={optionIndex} className={optionClass}>
                                <input
                                    type="radio"
                                    name={`question-${question.id}`}
                                    value={optionIndex}
                                    checked={isSelected}
                                    onChange={(e) => handleAnswerChange(question.id, parseInt(e.target.value))}
                                    className="text-blue-600 dark:text-blue-500"
                                />
                                <span>{option}</span>
                                {shouldShowResults && lastSubmission && wasSelected && (
                                    <span className="ml-2">
                                        {lastAnswer.is_correct ? '✓' : '✗'}
                                    </span>
                                )}
                            </label>
                        )})}
                        
                        {lastSubmission && showCorrectAnswer && correctAnswer && (
                            <div className="mt-4 p-3 bg-slate-50 dark:bg-slate-800/50 rounded border border-slate-200 dark:border-slate-700">
                                <div className="text-sm text-slate-600 dark:text-slate-400">
                                    Correct Answer:
                                </div>
                                <div className="mt-1 text-slate-800 dark:text-slate-200">
                                    {formatCorrectAnswer(question.id)}
                                </div>
                                {correctAnswer.explanation && (
                                    <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                                        <strong>Explanation:</strong> {correctAnswer.explanation}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {question.type === 'MSQ' && (
                    <div className="space-y-2">
                        {Array.isArray(question.options) && question.options.map((option, optionIndex) => {
                            const isSelected = Array.isArray(currentAnswer) && currentAnswer.includes(optionIndex);
                            const wasSelected = Array.isArray(lastAnswer?.answer) && lastAnswer.answer.includes(optionIndex);
                            let optionClass = "flex items-center space-x-3 p-2 rounded transition-colors ";
                            
                            if (shouldShowResults && lastSubmission && wasSelected) {
                                optionClass += lastAnswer?.is_correct
                                    ? "bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-400 " 
                                    : "bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-400 ";
                            } else {
                                optionClass += "hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200 ";
                            }
                            
                            return (
                                <label key={optionIndex} className={optionClass}>
                                    <input
                                        type="checkbox"
                                        value={optionIndex}
                                        checked={isSelected}
                                        onChange={(e) => {
                                            const value = parseInt(e.target.value);
                                            const currentAnswers = Array.isArray(currentAnswer) ? currentAnswer : [];
                                            handleAnswerChange(
                                                question.id,
                                                e.target.checked
                                                    ? [...currentAnswers, value]
                                                    : currentAnswers.filter(v => v !== value)
                                            );
                                        }}
                                        className="text-blue-600 dark:text-blue-500"
                                    />
                                    <span>{option}</span>
                                    {shouldShowResults && lastSubmission && wasSelected && (
                                        <span className="ml-2">
                                            {lastAnswer?.is_correct ? '✓' : '✗'}
                                        </span>
                                    )}
                                </label>
                            );
                        })}
                        
                        {showCorrectAnswer && correctAnswer && (
                            <div className="mt-4 p-3 bg-slate-50 dark:bg-slate-800/50 rounded border border-slate-200 dark:border-slate-700">
                                <div className="text-sm text-slate-600 dark:text-slate-400">
                                    Correct Answers:
                                </div>
                                <div className="mt-1 text-slate-800 dark:text-slate-200">
                                    {formatCorrectAnswer(question.id)}
                                </div>
                                {correctAnswer.explanation && (
                                    <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                                        <strong>Explanation:</strong> {correctAnswer.explanation}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {question.type === 'NUMERIC' && (
                    <div>
                        <input
                            type="number"
                            value={answers[question.id]}
                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                            className={`input-field ${
                                lastSubmission && lastAnswer
                                    ? lastAnswer?.is_correct
                                        ? 'border-green-300 dark:border-green-600 bg-green-50 dark:bg-green-900/20'
                                        : 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20'
                                    : 'border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-700'
                            } text-zinc-900 dark:text-white`}
                            step="any"
                            placeholder="Enter your answer..."
                        />
                        
                        {shouldShowResults && lastSubmission && (
                            <div className="mt-2">
                                <div className={`text-sm ${
                                    lastAnswer?.is_correct
                                        ? 'text-green-600 dark:text-green-400' 
                                        : 'text-red-600 dark:text-red-400'
                                }`}>
                                    Your answer: {lastAnswer?.answer} {lastAnswer?.is_correct ? '✓' : '✗'}
                                </div>
                                
                                {lastSubmission && showCorrectAnswer && correctAnswer && (
                                    <div className="mt-4 p-3 bg-slate-50 dark:bg-slate-800/50 rounded border border-slate-200 dark:border-slate-700">
                                        <div className="text-sm text-slate-600 dark:text-slate-400">
                                            Correct Answer:
                                        </div>
                                        <div className="mt-1 text-slate-800 dark:text-slate-200">
                                            {formatCorrectAnswer(question.id)}
                                        </div>
                                        {correctAnswer.explanation && (
                                            <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                                                <strong>Explanation:</strong> {correctAnswer.explanation}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* Update the bottom section to use the new condition */}
                {shouldShowResults && lastSubmission && (
                    <div className="mt-2 text-sm">
                        {questionScore === question.points ? (
                            <div className="text-green-600 dark:text-green-400">
                                ✓ Correct
                            </div>
                        ) : (
                            <div>
                                <div className="text-red-600 dark:text-red-400">
                                    ✗ Incorrect
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </Card>
        );
    };

    // Update submit button section
    const renderSubmitSection = () => {
        const isSubmittable = canSubmit();
        
        return (
            <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-zinc-800 border-t border-zinc-200 dark:border-zinc-700 p-4 shadow-md">
                <div className="max-w-4xl mx-auto flex justify-between items-center">
                    <div className="text-sm text-zinc-600 dark:text-zinc-400">
                        {assignment.type === 'practice' 
                            ? "This is a practice assignment. You can submit multiple times before the due date."
                            : "This is a graded assignment. You can submit multiple times before the due date, but no submissions after due date."
                        }
                        {!isSubmittable && (
                            <div className="text-red-600 dark:text-red-400">
                                Submission period has ended
                            </div>
                        )}
                    </div>
                    <button
                        onClick={handleSubmit}
                        disabled={submitting || !isSubmittable}
                        className={`px-6 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors
                            ${(submitting || !isSubmittable) ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        {submitting ? 'Submitting...' : 'Submit Assignment'}
                    </button>
                </div>
            </div>
        );
    };

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
        <div className="flex h-screen bg-zinc-50 dark:bg-zinc-900">
            {/* Left Sidebar - Course Structure */}
            {course && (
                <div className="w-80 bg-white dark:bg-zinc-800 shadow-lg dark:shadow-zinc-900/50 overflow-y-auto">
                    <div className="p-4 border-b dark:border-zinc-700">
                        <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">{course.code}</h2>
                        <p className="text-sm text-zinc-600 dark:text-zinc-400">{course.name}</p>

                        {/* Course Progress */}
                        <div className="mt-4 p-3 bg-zinc-50 dark:bg-zinc-700/50 rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Course Progress</span>
                                <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                                    {courseProgress?.percentage || 0}%
                                </span>
                            </div>
                            <div className="w-full bg-zinc-200 dark:bg-zinc-600 rounded-full h-2">
                                <div
                                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${courseProgress?.percentage || 0}%` }}
                                />
                            </div>
                            <div className="mt-2 flex items-center justify-between text-xs text-zinc-600 dark:text-zinc-400">
                                <span>{courseProgress?.completed_items || 0} completed</span>
                                <span>{courseProgress?.total_items || 0} total</span>
                            </div>
                        </div>
                    </div>

                    <nav className="p-2">
                        <div 
                            className="p-2 hover:bg-zinc-50 dark:hover:bg-zinc-700 cursor-pointer text-zinc-800 dark:text-zinc-200 transition-colors"
                            onClick={() => navigate(`/student/courses/${courseId}`)}
                        >
                            Course Introduction
                        </div>
                        
                        {course.weeks?.map(week => {
                            const weekProgress = courseProgress?.weeks?.find(w => w.week_id === week.id)?.progress || { percentage: 0 };
                            return (
                            <div key={week.id} className="mb-2">
                                    <div className="p-2 bg-zinc-50 dark:bg-zinc-700 font-medium text-zinc-800 dark:text-zinc-200 flex items-center justify-between">
                                        <span>Week {week.number}: {week.title}</span>
                                        <span className="text-xs text-zinc-600 dark:text-zinc-400">{weekProgress.percentage}%</span>
                                </div>
                                    {week.lectures?.map(lecture => {
                                        const isCompleted = lecture.completed;
                                        return (
                                    <button
                                        key={lecture.id}
                                                onClick={() => navigate(`/student/courses/${courseId}/lectures/${lecture.id}`)}
                                                className="w-full text-left p-2 pl-6 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors flex items-center justify-between group text-zinc-700 dark:text-zinc-300"
                                            >
                                                <div className="flex items-center">
                                                    {isCompleted && (
                                                        <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                                                    )}
                                                    <span>{lecture.title}</span>
                                                </div>
                                                {lecture.last_visited && (
                                                    <span className="text-xs text-zinc-500 dark:text-zinc-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        {new Date(lecture.last_visited).toLocaleDateString()}
                                                    </span>
                                                )}
                                    </button>
                                        );
                                    })}
                                    
                                    {week.assignments?.map(assignment => {
                                        const isActive = assignment.id === parseInt(assignmentId);
                                        const isCompleted = assignment.completed;
                                        return (
                                    <button
                                        key={assignment.id}
                                                onClick={() => navigate(`/student/courses/${courseId}/assignments/${assignment.id}`)}
                                                className={`w-full text-left p-2 pl-6 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors flex items-center justify-between group ${
                                                    isActive 
                                                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
                                                        : 'text-green-600 dark:text-green-500'
                                                }`}
                                            >
                                                <div className="flex items-center">
                                                    {isCompleted && (
                                                        <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                                                    )}
                                                    <span>📝 {assignment.title}</span>
                                                </div>
                                                {assignment.last_attempted && (
                                                    <span className="text-xs text-zinc-500 dark:text-zinc-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        {new Date(assignment.last_attempted).toLocaleDateString()}
                                                    </span>
                                                )}
                                    </button>
                                        );
                                    })}
                            </div>
                            );
                        })}
                    </nav>
                </div>
            )}

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="max-w-4xl mx-auto">
                    {/* Assignment Header */}
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-zinc-900 dark:text-white mb-4">
                            {assignment.title}
                            <span className={`ml-3 px-3 py-1 text-sm font-medium rounded-full ${
                                    assignment.type === 'practice' 
                                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400' 
                                        : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
                                }`}>
                                {assignment.type === 'practice' ? 'Practice' : 'Graded'}
                                </span>
                        </h2>
                        <div className="text-sm text-gray-600 mb-4">
                            <span className="mr-4">Type: {assignment?.type === 'practice' ? 'Practice' : 'Graded'}</span>
                            <span className="mr-4">Due Date: {assignment?.due_date ? new Date(assignment.due_date).toLocaleString() : 'No due date'}</span>
                        </div>
                        <div className="flex flex-col space-y-2 text-sm text-zinc-600 dark:text-zinc-400">
                            {renderSubmissionDetails()}
                                        </div>
                    </div>
                    /* NEW: Add Summary Section Here
                    {(!lastSubmission && assignment.type === 'practice') && (<div className="glass-card p-6 mb-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Assignment Guidance </h2>
                            <button
                                onClick={fetchSummary}
                                disabled={isSummarizing}
                                className="btn-primary flex items-center space-x-1"
                            >
                                {isSummarizing ? (
                                    <>
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        <span>Generating...</span>
                                    </>
                                ) : (
                                    <>
                                        <ClipboardDocumentListIcon className="w-4 h-4" />
                                        <span>Provide Guidance </span>
                                    </>
                                )}
                            </button>
                        </div>
  
                        {summaryError && (
                            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4 mb-4">
                                {summaryError}
                            </div>
                        )}
  
                        {summary ? (
                            <div className="prose dark:prose-invert max-w-none">
                                <p className="text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">{summary}</p>
                            </div>
                        ) : (
                            <div className="text-center text-zinc-500 dark:text-zinc-400 py-4">
                                {isSummarizing ? 'Generating guidance summary...' : 'No guidance summary generated yet. Click the button above to generate one.'}
                            </div>
                        )}
                    </div>)}

                    {/* Questions */}
                    <div className="space-y-6 mb-8">
                        {assignment.questions.map((question, index) => {
                            return renderQuestion(question, index);
                        })}
                    </div>

                    {renderSubmitSection()}
                </div>
            </div>
        </div>
    );
};

export default AssignmentView; 