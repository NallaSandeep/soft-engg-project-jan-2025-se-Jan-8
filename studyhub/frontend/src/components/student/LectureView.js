import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { Card } from '../common/Card';

const LectureView = () => {
    const { courseId, lectureId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [lecture, setLecture] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showTranscript, setShowTranscript] = useState(false);
    const [notes, setNotes] = useState('');
    const [isEditingNotes, setIsEditingNotes] = useState(false);
    const [tempNotes, setTempNotes] = useState('');

    useEffect(() => {
        fetchCourseAndLecture();
    }, [courseId, lectureId]);

    const fetchCourseAndLecture = async () => {
        try {
            setError(null);
            // Fetch course content for the sidebar
            const courseResponse = await courseApi.getCourseContent(courseId);
            if (courseResponse.success) {
                setCourse(courseResponse.data);
            }

            // Fetch lecture content
            const lectureResponse = await courseApi.getLectureContent(lectureId);
            if (lectureResponse.success) {
                setLecture(lectureResponse.data);
                // Load saved notes from localStorage
                const savedNotes = localStorage.getItem(`lecture-notes-${lectureId}`);
                if (savedNotes) {
                    setNotes(savedNotes);
                }
            } else {
                setError(lectureResponse.message || 'Failed to load lecture content');
            }
        } catch (err) {
            console.error('Error loading content:', err);
            setError(err.message || 'Failed to load content');
        } finally {
            setLoading(false);
        }
    };

    const handleNotesChange = (e) => {
        setTempNotes(e.target.value);
    };

    const saveNotes = () => {
        setNotes(tempNotes);
        localStorage.setItem(`lecture-notes-${lectureId}`, tempNotes);
        setIsEditingNotes(false);
    };

    const startEditingNotes = () => {
        setTempNotes(notes);
        setIsEditingNotes(true);
    };

    const cancelEditingNotes = () => {
        setTempNotes(notes);
        setIsEditingNotes(false);
    };

    // Extract video ID from YouTube URL
    const getYouTubeVideoId = (url) => {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const match = url?.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
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
                    onClick={() => navigate(`/courses/${courseId}`)}
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

    return (
        <div className="flex h-screen bg-zinc-50 dark:bg-zinc-900">
            {/* Left Sidebar - Course Structure */}
            <div className="w-64 bg-white dark:bg-zinc-800 shadow-lg dark:shadow-zinc-900/50 overflow-y-auto">
                <div className="p-4 border-b dark:border-zinc-700">
                    <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">{course.code}</h2>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400">{course.name}</p>
                </div>
                <nav className="p-2">
                    <div 
                        className="p-2 hover:bg-zinc-50 dark:hover:bg-zinc-700 cursor-pointer text-zinc-800 dark:text-zinc-200 transition-colors"
                        onClick={() => navigate(`/courses/${courseId}`)}
                    >
                        Course Introduction
                    </div>
                    {course.weeks?.map(week => (
                        <div key={week.id} className="mb-2">
                            <div className="p-2 bg-zinc-50 dark:bg-zinc-700 font-medium text-zinc-800 dark:text-zinc-200">
                                Week {week.number}: {week.title}
                            </div>
                            {week.lectures?.map(lec => (
                                <button
                                    key={lec.id}
                                    onClick={() => navigate(`/courses/${courseId}/lectures/${lec.id}`)}
                                    className={`w-full text-left p-2 pl-6 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors ${
                                        lec.id === parseInt(lectureId) 
                                            ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
                                            : 'text-zinc-700 dark:text-zinc-300'
                                    }`}
                                >
                                    {lec.title}
                                </button>
                            ))}
                            {week.assignments?.map(assignment => (
                                <button
                                    key={assignment.id}
                                    onClick={() => navigate(`/courses/${courseId}/assignments/${assignment.id}`)}
                                    className="w-full text-left p-2 pl-6 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 flex items-center text-green-600 dark:text-green-500 hover:text-green-800 dark:hover:text-green-400 transition-colors"
                                >
                                    <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    {assignment.title}
                                </button>
                            ))}
                        </div>
                    ))}
                </nav>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto">
                {/* Video Section */}
                <Card className="dark:bg-zinc-800">
                    <div className="p-4 border-b dark:border-zinc-700">
                        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">{lecture.title}</h1>
                        {lecture.description && (
                            <p className="text-zinc-600 dark:text-zinc-400 mt-2">{lecture.description}</p>
                        )}
                    </div>
                    <div className="max-w-5xl mx-auto p-4">
                        <div className="relative" style={{ paddingTop: '56.25%', height: '0' }}>
                            <iframe
                                src={`https://www.youtube.com/embed/${videoId}`}
                                title={lecture.title}
                                frameBorder="0"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                                className="absolute top-0 left-0 w-full h-full"
                                style={{ minHeight: '480px' }}
                            ></iframe>
                        </div>
                    </div>
                </Card>

                {/* Transcript Section */}
                <Card className="mt-4 shadow-sm max-w-5xl mx-auto dark:bg-zinc-800">
                    <button
                        onClick={() => setShowTranscript(!showTranscript)}
                        className="w-full p-4 text-left font-semibold flex justify-between items-center hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-900 dark:text-white transition-colors"
                    >
                        <span>Lecture Transcript</span>
                        <span className="text-zinc-500 dark:text-zinc-400">{showTranscript ? '▼' : '▶'}</span>
                    </button>
                    {showTranscript && (
                        <div className="p-4 border-t dark:border-zinc-700">
                            <div className="prose dark:prose-invert max-w-none text-zinc-800 dark:text-zinc-300">
                                {lecture.transcript || 'No transcript available for this lecture.'}
                            </div>
                        </div>
                    )}
                </Card>

                {/* Notes Section */}
                <Card className="mt-4 shadow-sm p-4 max-w-5xl mx-auto mb-8 dark:bg-zinc-800">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Your Notes</h2>
                        <div className="space-x-2">
                            {!isEditingNotes ? (
                                <button
                                    onClick={startEditingNotes}
                                    className="px-3 py-1 text-sm bg-blue-600 dark:bg-blue-700 text-white rounded hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
                                >
                                    Edit Notes
                                </button>
                            ) : (
                                <>
                                    <button
                                        onClick={saveNotes}
                                        className="px-3 py-1 text-sm bg-green-600 dark:bg-green-700 text-white rounded hover:bg-green-700 dark:hover:bg-green-600 transition-colors"
                                    >
                                        Save
                                    </button>
                                    <button
                                        onClick={cancelEditingNotes}
                                        className="px-3 py-1 text-sm bg-zinc-600 dark:bg-zinc-700 text-white rounded hover:bg-zinc-700 dark:hover:bg-zinc-600 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                    <p className="text-zinc-600 dark:text-zinc-400 text-sm mb-2">
                        Take notes while watching the video. Click "Edit Notes" to make changes.
                    </p>
                    {isEditingNotes ? (
                        <textarea
                            value={tempNotes}
                            onChange={handleNotesChange}
                            className="w-full p-2 border dark:border-zinc-600 rounded-md bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                            rows="6"
                            placeholder="Start typing your notes here..."
                        ></textarea>
                    ) : (
                        <div className="w-full p-2 border dark:border-zinc-600 rounded-md bg-zinc-50 dark:bg-zinc-700 min-h-[150px] whitespace-pre-wrap text-zinc-800 dark:text-zinc-200">
                            {notes || 'No notes yet. Click "Edit Notes" to start taking notes.'}
                        </div>
                    )}
                </Card>
            </div>
        </div>
    );
};

export default LectureView; 