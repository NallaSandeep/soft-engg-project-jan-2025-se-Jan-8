import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { Card } from '../common/Card';
import { CheckCircleIcon, ChevronDownIcon, ChevronUpIcon, DocumentTextIcon, PlayIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/outline';

const LectureView = () => {
    const { courseId, lectureId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [lecture, setLecture] = useState(null);
    const [courseProgress, setCourseProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showTranscript, setShowTranscript] = useState(false);
    const [notes, setNotes] = useState('');
    const [pdfUrl, setPdfUrl] = useState(null);
    const [pdfError, setPdfError] = useState(false);
    const [summary, setSummary] = useState(null);
    const [isSummarizing, setIsSummarizing] = useState(false);
    const [summaryError, setSummaryError] = useState(null);

    useEffect(() => {
        setSummary(null);
        fetchLectureContent();
    }, [courseId, lectureId]);

    const fetchLectureContent = async () => {
        try {
            setLoading(true);
            const [courseResponse, lectureResponse, progressResponse] = await Promise.all([
                courseApi.getCourseContent(courseId),
                courseApi.getLectureContent(lectureId),
                courseApi.getCourseProgress(courseId)
            ]);

            console.log('DEBUG - Lecture Response:', {
                success: lectureResponse.success,
                data: lectureResponse.data,
                type: lectureResponse.type,
                contentType: lectureResponse.data?.content_type
            });

            if (courseResponse.success) {
                setCourse(courseResponse.data);
            }

            // Handle lecture response based on its type
            if (lectureResponse) {
                if (lectureResponse.type === 'pdf') {
                    setLecture({
                        id: parseInt(lectureId),
                        content_type: 'pdf',
                        title: course?.weeks?.flatMap(w => w.lectures)?.find(l => l.id === parseInt(lectureId))?.title || 'Lecture',
                        file_path: lectureResponse.url,
                        transcript: lectureResponse.transcript
                    });
                    
                    // Immediately trigger PDF loading
                    try {
                        console.log('Fetching PDF file...');
                        const pdfResponse = await courseApi.getLecturePdf(lectureId);
                        console.log('PDF response received');
                        
                        if (pdfResponse && pdfResponse.data) {
                            const blob = new Blob([pdfResponse.data], { type: 'application/pdf' });
                            const url = window.URL.createObjectURL(blob);
                            console.log('Created blob URL for PDF:', url);
                            setPdfUrl(url);
                            setPdfError(false);
                        }
                    } catch (error) {
                        console.error('Error loading PDF:', error);
                        setPdfError(true);
                    }
                } else if (lectureResponse.type === 'youtube') {
                    setLecture({
                        id: parseInt(lectureId),
                        content_type: 'youtube',
                        title: course?.weeks?.flatMap(w => w.lectures)?.find(l => l.id === parseInt(lectureId))?.title || 'Lecture',
                        youtube_url: lectureResponse.url,
                        transcript: lectureResponse.transcript
                    });
                }
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

    const getYouTubeVideoId = (url) => {
        if (!url) return null;
        const match = url.match(/[?&]v=([^&]+)/);
        return match ? match[1] : null;
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

    if (!lecture || !course) return (
        <div className="text-center p-4 text-zinc-600 dark:text-zinc-400">Content not found</div>
    );

    const videoId = getYouTubeVideoId(lecture.youtube_url);

    const renderPdfContent = () => {
        if (lecture?.content_type !== 'pdf') return null;

        return (
            <div className="pdf-container" style={{ width: '100%', height: '600px', position: 'relative' }}>
                {!pdfError ? (
                    pdfUrl ? (
                        <object
                            data={pdfUrl}
                            type="application/pdf"
                            style={{ width: '100%', height: '100%' }}
                            allow="fullscreen"
                        >
                            <embed
                                src={pdfUrl}
                                type="application/pdf"
                                style={{ width: '100%', height: '100%' }}
                                className="w-full h-full"
                                allow="fullscreen"
                            />
                            <p className="text-center mt-4">
                                PDF cannot be displayed. <a href={pdfUrl} download className="text-blue-500 hover:text-blue-700">Download PDF</a>
                            </p>
                        </object>
                    ) : (
                        <div className="flex justify-center items-center h-full">
                            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                            <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading PDF...</span>
                        </div>
                    )
                ) : (
                    <div id="pdf-error" className="text-center mt-8 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <p className="text-red-600 dark:text-red-400 mb-4">Unable to display PDF directly. Click below to download:</p>
                        <button
                            onClick={async () => {
                                try {
                                    console.log('Downloading PDF...');
                                    const response = await courseApi.getLecturePdf(lecture.id);
                                    console.log('Download response received');
                                    
                                    const blob = new Blob([response.data], { type: 'application/pdf' });
                                    const url = window.URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = `${lecture.title}.pdf`;
                                    document.body.appendChild(a);
                                    a.click();
                                    window.URL.revokeObjectURL(url);
                                    document.body.removeChild(a);
                                    console.log('PDF download completed');
                                } catch (error) {
                                    console.error('Error downloading PDF:', error);
                                    console.error('Download error details:', {
                                        message: error.message,
                                        response: error.response,
                                        status: error.response?.status
                                    });
                                    alert('Failed to download PDF. Please try again.');
                                }
                            }}
                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition-colors"
                        >
                            Download PDF
                        </button>
                    </div>
                )}
            </div>
        );
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
                    message: `Please summarize this transcript content in 100 words. Don't return any mark down characters. Instead use numbering: ${JSON.stringify(lecture.transcript)}`
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
                        <div className="w-full bg-zinc-200 dark:bg-zinc-600 rounded-full h-1.5">
                            <div 
                                className="bg-blue-500 h-1.5 rounded-full transition-all duration-300" 
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
                                    const isActive = lecture.id === parseInt(lectureId);
                                    const isCompleted = lecture.completed;
                                    return (
                                        <button
                                            key={lecture.id}
                                            onClick={() => navigate(`/student/courses/${courseId}/lectures/${lecture.id}`)}
                                            className={`w-full text-left p-2 pl-6 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors flex items-center justify-between group ${
                                                isActive 
                                                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
                                                    : 'text-zinc-700 dark:text-zinc-300'
                                            }`}
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
                                    const isCompleted = assignment.completed;
                                    return (
                                        <button
                                            key={assignment.id}
                                            onClick={() => navigate(`/student/courses/${courseId}/assignments/${assignment.id}`)}
                                            className="w-full text-left p-2 pl-6 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors flex items-center justify-between group text-green-600 dark:text-green-500"
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
            <div className="flex-1 overflow-y-auto">
                <div className="max-w-5xl mx-auto p-4 lg:px-8">
                    {/* Lecture Header */}
                    <Card className="mb-4">
                        <div className="p-4">
                            <div className="flex items-center justify-between">
                                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">{lecture.title}</h1>
                                <div className="flex items-center space-x-4">
                                    <span className="text-sm text-zinc-600 dark:text-zinc-400">
                                        Last visited: {new Date(lecture.last_visited || Date.now()).toLocaleDateString()}
                                    </span>
                                    {lecture.completed && (
                                        <span className="text-sm text-green-600 dark:text-green-500 flex items-center">
                                            <CheckCircleIcon className="h-5 w-5 mr-1" />
                                            Completed
                                        </span>
                                    )}
                                </div>
                            </div>
                            <p className="mt-1 text-zinc-600 dark:text-zinc-400">{lecture.description}</p>
                        </div>
                    </Card>

                    {/* Content Display */}
                    <Card className="mb-4 overflow-hidden">
                        <div className="relative" style={{ height: "calc(100vh - 300px)" }}>
                            {lecture?.content_type === 'youtube' && lecture.youtube_url && (
                                <iframe
                                    src={`https://www.youtube.com/embed/${getYouTubeVideoId(lecture.youtube_url)}`}
                                    title={lecture.title}
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                                    allowFullScreen
                                    className="absolute inset-0 w-full h-full"
                                ></iframe>
                            )}
                            {lecture?.content_type === 'pdf' && renderPdfContent()}
                        </div>
                    </Card>

                    {/* Transcript Section */}
                    <Card className="mb-4">
                        <button
                            onClick={() => setShowTranscript(!showTranscript)}
                            className="w-full p-4 flex items-center justify-between text-zinc-900 dark:text-white"
                        >
                            <span className="text-lg font-medium">Lecture Transcript</span>
                            {showTranscript ? (
                                <ChevronUpIcon className="h-5 w-5" />
                            ) : (
                                <ChevronDownIcon className="h-5 w-5" />
                            )}
                        </button>
                        {showTranscript && (
                            <div className="px-4 pb-4">
                                <p className="text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">
                                    {lecture.transcript}
                                </p>
                            </div>
                        )}
                    </Card>

                    {/* Notes Section */}
                    {/* <Card className="mb-4">
                        <div className="p-4">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-medium text-zinc-900 dark:text-white">Your Notes</h2>
                                <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300">
                                    Edit Notes
                                </button>
                            </div>
                            {notes ? (
                                <p className="text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">{notes}</p>
                            ) : (
                                <p className="text-zinc-500 dark:text-zinc-400">No notes taken yet.</p>
                            )}
                        </div>
                    </Card> */}                    
                    
                    {/* NEW: Add Summary Section Here */}
                    <div className="glass-card p-6 mb-6">
                      <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Lecture Summary</h2>
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
                </div>
            </div>
        </div>
    );
};

export default LectureView; 