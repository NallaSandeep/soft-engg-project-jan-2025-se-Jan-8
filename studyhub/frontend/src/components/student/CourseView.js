import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import ReactMarkdown from 'react-markdown';
import { Card } from '../common/Card';
import { ChartBarIcon, CheckCircleIcon, DocumentTextIcon, PlayIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/outline';

const CourseView = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeSection, setActiveSection] = useState('introduction');

    const [summary, setSummary] = useState(null);
    const [isSummarizing, setIsSummarizing] = useState(false);
    const [summaryError, setSummaryError] = useState(null);

    const [practiceSuggestions, setPracticeSuggestions] = useState(null); // Updated to string
    const [isFetchingSuggestions, setIsFetchingSuggestions] = useState(false);
    const [suggestionsError, setSuggestionsError] = useState(null);

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            setError(null);
            const [courseResponse, progressResponse] = await Promise.all([
                courseApi.getCourseContent(courseId),
                courseApi.getCourseProgress(courseId)
            ]);

            if (courseResponse.success) {
                setCourse(courseResponse.data);
            } else {
                setError(courseResponse.message || 'Failed to load course content');
            }

            if (progressResponse.success) {
                setProgress(progressResponse.data);
            }
        } catch (err) {
            console.error('Error loading course:', err);
            setError(err.message || 'Failed to load course content');
        } finally {
            setLoading(false);
        }
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
                    message: `Please summarize this course content: ${JSON.stringify(contentToSummarize)}`
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

    const fetchPracticeSuggestions = async () => {
        setIsFetchingSuggestions(true);
        setSuggestionsError(null);

        try {
            const contentToAnalyze = {
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
                    message: `Suggest practice assignments based on this course content: ${JSON.stringify(contentToAnalyze)}`
                })
            });

            if (!response.ok) throw new Error('Failed to fetch suggestions');
            const data = await response.json();
            console.log('Suggestions:', data.content || data.response);
            setPracticeSuggestions(data.content || data.response || "No suggestions available."); // Updated to handle multi-line text
        } catch (err) {
            console.error('Error fetching practice suggestions:', err);
            setSuggestionsError('Failed to fetch practice assignment suggestions');
        } finally {
            setIsFetchingSuggestions(false);
        }
    };


    if (loading) return (
        <div className="flex justify-center items-center h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading course content...</span>
        </div>
    );
    
    if (error) return (
        <div className="text-red-500 dark:text-red-400 text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            {error}
        </div>
    );
    
    if (!course) return (
        <div className="text-center p-4 text-zinc-600 dark:text-zinc-400">Course not found</div>
    );

    return (
        <div className="flex h-screen bg-zinc-50 dark:bg-zinc-900">
            {/* Left Sidebar - Course Structure */}
            <div className="w-80 bg-white dark:bg-zinc-800 shadow-lg dark:shadow-zinc-900/50 overflow-y-auto">
                {/* Course Header */}
                <div className="p-4 border-b dark:border-zinc-700">
                    <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">{course.code}</h2>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400">{course.name}</p>
                    
                    {/* Mini Progress Report */}
                    <div className="mt-4 p-3 bg-zinc-50 dark:bg-zinc-700/50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Course Progress</span>
                            <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">{progress?.percentage || 0}%</span>
                        </div>
                        <div className="w-full bg-zinc-200 dark:bg-zinc-600 rounded-full h-1.5">
                            <div 
                                className="bg-blue-500 h-1.5 rounded-full transition-all duration-300" 
                                style={{ width: `${progress?.percentage || 0}%` }}
                            />
                        </div>
                        <div className="mt-2 flex items-center justify-between text-xs text-zinc-600 dark:text-zinc-400">
                            <span>{progress?.completed_items || 0} completed</span>
                            <span>{progress?.total_items || 0} total</span>
                        </div>
                    </div>
                </div>
                
                <nav className="p-2">
                    <button
                        onClick={() => setActiveSection('introduction')}
                        className={`w-full text-left p-2 rounded transition-colors ${
                            activeSection === 'introduction' 
                                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
                                : 'hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200'
                        }`}
                    >
                        Course Introduction 
                    </button>
                    
                    {course.weeks?.map(week => {
                        const weekProgress = progress?.weeks?.find(w => w.week_id === week.id)?.progress || { percentage: 0 };
                        return (
                            <div key={week.id} className="mb-2">
                                <div className="p-2 bg-zinc-50 dark:bg-zinc-700 font-medium text-zinc-800 dark:text-zinc-200 flex items-center justify-between">
                                    <span>Week {week.number}: {week.title}</span>
                                    <span className="text-xs text-zinc-600 dark:text-zinc-400">{weekProgress.percentage}%</span>
                                </div>
                                {week.lectures?.map(lecture => {
                                    const isCompleted = lecture.completed;
                                    const lastVisited = lecture.last_visited;
                                    return (
                                        <button
                                            key={lecture.id}
                                            onClick={() => navigate(`/student/courses/${courseId}/lectures/${lecture.id}`)}
                                            className="w-full text-left p-2 pl-6 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-300 transition-colors flex items-center justify-between group"
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
                                            {lastVisited && (
                                                <span className="text-xs text-zinc-500 dark:text-zinc-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    {new Date(lastVisited).toLocaleDateString()}
                                                </span>
                                            )}
                                        </button>
                                    );
                                })}
                                
                                {week.assignments?.map(assignment => {
                                    const isCompleted = assignment.completed;
                                    const lastAttempted = assignment.last_attempted;
                                    return (
                                        <button
                                            key={assignment.id}
                                            onClick={() => navigate(`/student/courses/${courseId}/assignments/${assignment.id}`)}
                                            className="w-full text-left p-2 pl-6 text-sm text-green-600 dark:text-green-500 hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors flex items-center justify-between group"
                                        >
                                            <div className="flex items-center">
                                                {isCompleted && (
                                                    <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                                                )}
                                                <ClipboardDocumentListIcon className="h-4 w-4 text-green-500 mr-2" />
                                                <span>{assignment.title}</span>
                                            </div>
                                            {lastAttempted && (
                                                <span className="text-xs text-zinc-500 dark:text-zinc-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    {new Date(lastAttempted).toLocaleDateString()}
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
            <div className="flex-1 overflow-y-auto">
                {activeSection === 'introduction' ? (
                    <Card className="m-4 p-6 dark:bg-zinc-800">
                        <h1 className="text-3xl font-bold mb-4 text-zinc-900 dark:text-white">{course.name}</h1>
                        <div className="mb-6">
                            <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 px-3 py-1 rounded-full text-sm">
                                {course.code}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-6 mb-8">
                            <div>
                                <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">Course Faculty</h3>
                                <p className="text-zinc-600 dark:text-zinc-400">{course.created_by}</p>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">Course Duration</h3>
                                <p className="text-zinc-600 dark:text-zinc-400">
                                    {new Date(course.start_date).toLocaleDateString()} - {new Date(course.end_date).toLocaleDateString()}
                                </p>
                            </div>
                        </div>

                        <div className="prose dark:prose-invert max-w-none">
                            <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Course Description</h2>
                            <ReactMarkdown>{course.description}</ReactMarkdown>
                        </div>

                        <div className="mt-8">
                            <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Course Structure</h2>
                            <div className="space-y-4">
                                {course.weeks?.map(week => {
                                    const weekProgress = progress?.weeks?.find(w => w.week_id === week.id)?.progress || { percentage: 0 };
                                    return (
                                        <div key={week.id} className="border dark:border-zinc-700 rounded-lg p-4 bg-white dark:bg-zinc-700/50">
                                            <div className="flex items-center justify-between mb-2">
                                                <h3 className="font-medium text-zinc-900 dark:text-white">
                                                    Week {week.number}: {week.title}
                                                </h3>
                                                <span className="text-sm text-zinc-600 dark:text-zinc-400">
                                                    {weekProgress.percentage}% Complete
                                                </span>
                                            </div>
                                            <div className="w-full bg-zinc-200 dark:bg-zinc-600 rounded-full h-1 mb-3">
                                                <div 
                                                    className="bg-blue-500 h-1 rounded-full transition-all duration-300" 
                                                    style={{ width: `${weekProgress.percentage}%` }}
                                                />
                                            </div>
                                            <p className="text-zinc-600 dark:text-zinc-400 text-sm mb-2">{week.description}</p>
                                            <div className="pl-4 space-y-1">
                                                {week.lectures?.map(lecture => (
                                                    <div key={lecture.id} className="text-sm py-1 text-zinc-800 dark:text-zinc-300 flex items-center">
                                                        {lecture.completed && (
                                                            <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                                                        )}
                                                        <span>• {lecture.title}</span>
                                                    </div>
                                                ))}
                                                {week.assignments?.map(assignment => (
                                                    <div key={assignment.id} className="text-sm py-1 text-green-600 dark:text-green-500 flex items-center">
                                                        {assignment.completed && (
                                                            <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                                                        )}
                                                        <span>:memo: {assignment.title}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </Card>
                ) : null}


            {/* Course Info */}
<div className="glass-card p-6 mb-6">
  {/* ... existing course info content ... */}
</div>

{/* NEW: Add Summary Section Here */}
<div className="glass-card p-6 mb-6">
  <div className="flex justify-between items-center mb-4">
    <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Course Summary</h2>
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
          <span>Generate Summary </span>
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
      {isSummarizing ? 'Generating summary...' : 'No summary generated yet. Click the button above to generate one.'}
    </div>
  )}
</div>

{/* Weeks */}
<div className="space-y-6">
  {/* ... existing weeks content ... */}
</div>

{/* NEW: Add Practice Assignment Suggestions Section Here */}
<div className="glass-card p-6 mb-6">
    <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Practice Assignment Suggestions</h2>
        <button
            onClick={fetchPracticeSuggestions}
            disabled={isFetchingSuggestions}
            className="btn-primary flex items-center space-x-1"
        >
            {isFetchingSuggestions ? (
                <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Fetching...</span>
                </>
            ) : (
                <>
                    <ClipboardDocumentListIcon className="w-4 h-4" />
                    <span>Get Suggestions</span>
                </>
            )}
        </button>
    </div>

    {suggestionsError && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4 mb-4">
            {suggestionsError}
        </div>
    )}

    {practiceSuggestions ? (
        <div className="prose dark:prose-invert max-w-none bg-zinc-50 dark:bg-zinc-800 p-4 rounded-lg border border-zinc-200 dark:border-zinc-700 shadow-sm">
            <pre className="whitespace-pre-wrap text-zinc-700 dark:text-zinc-300 font-mono text-sm leading-relaxed">
                {practiceSuggestions}
            </pre>
        </div>
    ) : (
        <div className="text-center text-zinc-500 dark:text-zinc-400 py-4">
            {isFetchingSuggestions ? 'Fetching suggestions...' : 'No suggestions available. Click the button above to fetch suggestions.'}
        </div>
    )}
</div>





            </div>
        </div>
    );
};

export default CourseView;