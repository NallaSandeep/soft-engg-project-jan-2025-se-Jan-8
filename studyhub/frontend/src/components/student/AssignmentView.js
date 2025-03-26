import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { Card } from '../common/Card';
import { CheckCircleIcon, ClockIcon, DocumentTextIcon, PlayIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/outline';

const AssignmentView = () => {
    const { courseId, assignmentId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [assignment, setAssignment] = useState(null);
    const [courseProgress, setCourseProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [answers, setAnswers] = useState({});
    const [submitted, setSubmitted] = useState(false);

    useEffect(() => {
        fetchAssignmentContent();
    }, [courseId, assignmentId]);

    const fetchAssignmentContent = async () => {
        try {
            setLoading(true);
            const [courseResponse, assignmentResponse, progressResponse] = await Promise.all([
                courseApi.getCourseContent(courseId),
                courseApi.getAssignmentContent(assignmentId),
                courseApi.getCourseProgress(courseId)
            ]);

            if (courseResponse.success) {
                setCourse(courseResponse.data);
            }

            if (assignmentResponse.success) {
                setAssignment(assignmentResponse.data);
                // Initialize answers object
                const initialAnswers = {};
                assignmentResponse.data.questions.forEach(q => {
                    initialAnswers[q.id] = q.type === 'multiple_choice' ? '' : [];
                });
                setAnswers(initialAnswers);
            }

            if (progressResponse.success) {
                setCourseProgress(progressResponse.data);
            }
        } catch (err) {
            setError('Failed to load content');
            console.error('Error loading content:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswerChange = (questionId, value, type) => {
        if (type === 'multiple_choice') {
            setAnswers(prev => ({ ...prev, [questionId]: value }));
        } else if (type === 'multiple_select') {
            setAnswers(prev => {
                const currentAnswers = prev[questionId] || [];
                if (currentAnswers.includes(value)) {
                    return {
                        ...prev,
                        [questionId]: currentAnswers.filter(v => v !== value)
                    };
                } else {
                    return {
                        ...prev,
                        [questionId]: [...currentAnswers, value]
                    };
                }
            });
        }
    };

    const handleSubmit = async () => {
        try {
            const response = await courseApi.submitAssignment(assignmentId, answers);
            if (response.success) {
                setSubmitted(true);
                // Refresh progress data
                const progressResponse = await courseApi.getCourseProgress(courseId);
                if (progressResponse.success) {
                    setCourseProgress(progressResponse.data);
                }
                // Update assignment completion status
                setAssignment(prev => ({
                    ...prev,
                    completed: true,
                    last_attempted: new Date().toISOString()
                }));
            }
        } catch (err) {
            console.error('Error submitting assignment:', err);
        }
    };

    if (loading) return (
        <div className="flex justify-center items-center h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading content...</span>
        </div>
    );
    
    if (error) return (
        <div className="flex flex-col items-center justify-center h-screen">
            <div className="text-red-500 dark:text-red-400 text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <h2 className="text-xl font-bold mb-2 text-red-700 dark:text-red-300">Error Loading Content</h2>
                <p>{error}</p>
                <button
                    onClick={() => navigate(`/student/courses/${courseId}`)}
                    className="mt-4 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                >
                    ← Back to Course
                </button>
            </div>
        </div>
    );
    
    if (!assignment || !course) return (
        <div className="text-center p-4 text-zinc-600 dark:text-zinc-400">Content not found</div>
    );

    return (
        <div className="flex h-screen bg-zinc-50 dark:bg-zinc-900">
            {/* Left Sidebar - Course Structure */}
            <div className="w-80 flex-shrink-0 bg-white dark:bg-zinc-800 shadow-lg dark:shadow-zinc-900/50 overflow-y-auto">
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
                                                {lecture.content_type === 'pdf' ? (
                                                    <DocumentTextIcon className="h-4 w-4 text-blue-500 mr-2" />
                                                ) : (
                                                    <PlayIcon className="h-4 w-4 text-blue-500 mr-2" />
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
                                                <ClipboardDocumentListIcon className="h-4 w-4 text-green-500 mr-2" />
                                                <span>{assignment.title}</span>
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

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="max-w-5xl mx-auto lg:px-8">
                    {/* Course Progress Card */}
                    <Card className="mb-4 bg-white dark:bg-zinc-800">
                        <div className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">{course.code}</h2>
                                    <p className="text-sm text-zinc-600 dark:text-zinc-400">Course Progress</p>
                                </div>
                                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                    {courseProgress?.percentage || 0}%
                                </div>
                            </div>
                            <div className="mt-4">
                                <div className="w-full bg-zinc-200 dark:bg-zinc-600 rounded-full h-2">
                                    <div 
                                        className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                                        style={{ width: `${courseProgress?.percentage || 0}%` }}
                                    />
                                </div>
                                <div className="mt-2 flex items-center justify-between text-sm text-zinc-600 dark:text-zinc-400">
                                    <span>{courseProgress?.completed_items || 0} completed</span>
                                    <span>{courseProgress?.total_items || 0} total items</span>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Assignment Header */}
                    <Card className="mb-4">
                        <div className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">{assignment.title}</h1>
                                    <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">{assignment.description}</p>
                                </div>
                                <div className="flex items-center space-x-4">
                                    {assignment.last_attempted && (
                                        <div className="flex items-center text-sm text-zinc-600 dark:text-zinc-400">
                                            <ClockIcon className="h-4 w-4 mr-1" />
                                            <span>Last attempt: {new Date(assignment.last_attempted).toLocaleDateString()}</span>
                                        </div>
                                    )}
                                    <div className="flex items-center text-sm">
                                        <DocumentTextIcon className="h-4 w-4 mr-1" />
                                        <span className={assignment.type === 'practice' ? 'text-blue-600 dark:text-blue-400' : 'text-green-600 dark:text-green-500'}>
                                            {assignment.type === 'practice' ? 'Practice' : 'Graded'}
                                        </span>
                                    </div>
                                    {assignment.completed && (
                                        <span className="flex items-center text-green-600 dark:text-green-500">
                                            <CheckCircleIcon className="h-5 w-5 mr-1" />
                                            Completed
                                        </span>
                                    )}
                                </div>
                            </div>
                            <div className="mt-4 flex items-center justify-between text-sm text-zinc-600 dark:text-zinc-400">
                                <div>Total Points: {assignment.total_points}</div>
                                <div>Due: {new Date(assignment.due_date).toLocaleString()}</div>
                            </div>
                        </div>
                    </Card>

                    {/* Questions */}
                    <div className="space-y-4">
                        {assignment.questions.map((question, index) => (
                            <Card key={question.id} className="overflow-hidden">
                                <div className="p-4">
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-lg font-medium text-zinc-900 dark:text-white">
                                            Question {index + 1}: {question.title}
                                        </h3>
                                        <span className="text-sm text-zinc-600 dark:text-zinc-400">
                                            {question.points} {question.points === 1 ? 'point' : 'points'}
                                        </span>
                                    </div>
                                    <p className="text-zinc-700 dark:text-zinc-300 mb-4">{question.content}</p>
                                    
                                    {question.type === 'multiple_choice' ? (
                                        <div className="space-y-2">
                                            {question.options.map((option, optionIndex) => (
                                                <label
                                                    key={optionIndex}
                                                    className="flex items-center p-3 rounded-lg bg-zinc-50 dark:bg-zinc-700/50 hover:bg-zinc-100 dark:hover:bg-zinc-700 cursor-pointer transition-colors"
                                                >
                                                    <input
                                                        type="radio"
                                                        name={`question-${question.id}`}
                                                        value={option}
                                                        checked={answers[question.id] === option}
                                                        onChange={() => handleAnswerChange(question.id, option, 'multiple_choice')}
                                                        className="mr-3"
                                                    />
                                                    <span className="text-zinc-700 dark:text-zinc-300">{option}</span>
                                                </label>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="space-y-2">
                                            {question.options.map((option, optionIndex) => (
                                                <label
                                                    key={optionIndex}
                                                    className="flex items-center p-3 rounded-lg bg-zinc-50 dark:bg-zinc-700/50 hover:bg-zinc-100 dark:hover:bg-zinc-700 cursor-pointer transition-colors"
                                                >
                                                    <input
                                                        type="checkbox"
                                                        value={option}
                                                        checked={(answers[question.id] || []).includes(option)}
                                                        onChange={() => handleAnswerChange(question.id, option, 'multiple_select')}
                                                        className="mr-3"
                                                    />
                                                    <span className="text-zinc-700 dark:text-zinc-300">{option}</span>
                                                </label>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </Card>
                        ))}
                    </div>

                    {/* Submit Button */}
                    <div className="mt-6 flex items-center justify-between">
                        <p className="text-sm text-zinc-600 dark:text-zinc-400">
                            {assignment.type === 'practice' 
                                ? 'This is a practice assignment. You can submit multiple times.' 
                                : 'This is a graded assignment. You can only submit once.'}
                        </p>
                        <button
                            onClick={handleSubmit}
                            disabled={submitted}
                            className={`px-6 py-2 rounded-lg text-white transition-colors ${
                                submitted
                                    ? 'bg-green-500 cursor-not-allowed'
                                    : 'bg-blue-500 hover:bg-blue-600'
                            }`}
                        >
                            {submitted ? 'Submitted' : 'Submit Assignment'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssignmentView; 