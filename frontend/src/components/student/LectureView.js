import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

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

    if (loading) return <div className="flex justify-center items-center h-screen">Loading content...</div>;
    if (error) return (
        <div className="flex flex-col items-center justify-center h-screen">
            <div className="text-red-500 text-center p-4">
                <h2 className="text-xl font-bold mb-2">Error Loading Content</h2>
                <p>{error}</p>
                <button
                    onClick={() => navigate(`/courses/${courseId}`)}
                    className="mt-4 text-blue-600 hover:text-blue-800"
                >
                    ← Back to Course
                </button>
            </div>
        </div>
    );
    if (!lecture || !course) return <div className="text-center p-4">Content not found</div>;

    const videoId = getYouTubeVideoId(lecture.youtube_url);

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Left Sidebar - Course Structure */}
            <div className="w-64 bg-white shadow-lg overflow-y-auto">
                <div className="p-4 border-b">
                    <h2 className="text-lg font-semibold">{course.code}</h2>
                    <p className="text-sm text-gray-600">{course.name}</p>
                </div>
                <nav className="p-2">
                    <div 
                        className="p-2 hover:bg-gray-50 cursor-pointer"
                        onClick={() => navigate(`/courses/${courseId}`)}
                    >
                        Course Introduction
                    </div>
                    {course.weeks?.map(week => (
                        <div key={week.id} className="mb-2">
                            <div className="p-2 bg-gray-50 font-medium">
                                Week {week.number}: {week.title}
                            </div>
                            {week.lectures?.map(lec => (
                                <button
                                    key={lec.id}
                                    onClick={() => navigate(`/courses/${courseId}/lectures/${lec.id}`)}
                                    className={`w-full text-left p-2 pl-6 text-sm hover:bg-gray-50 ${
                                        lec.id === parseInt(lectureId) ? 'bg-blue-50 text-blue-600' : ''
                                    }`}
                                >
                                    {lec.title}
                                </button>
                            ))}
                            {week.assignments?.map(assignment => (
                                <button
                                    key={assignment.id}
                                    onClick={() => navigate(`/courses/${courseId}/assignments/${assignment.id}`)}
                                    className="w-full text-left p-2 pl-6 text-sm hover:bg-gray-50 flex items-center text-green-600 hover:text-green-800"
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
                <div className="bg-white">
                    <div className="p-4 border-b">
                        <h1 className="text-2xl font-bold">{lecture.title}</h1>
                        {lecture.description && (
                            <p className="text-gray-600 mt-2">{lecture.description}</p>
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
                </div>

                {/* Transcript Section */}
                <div className="bg-white mt-4 shadow-sm max-w-5xl mx-auto">
                    <button
                        onClick={() => setShowTranscript(!showTranscript)}
                        className="w-full p-4 text-left font-semibold flex justify-between items-center hover:bg-gray-50"
                    >
                        <span>Lecture Transcript</span>
                        <span className="text-gray-500">{showTranscript ? '▼' : '▶'}</span>
                    </button>
                    {showTranscript && (
                        <div className="p-4 border-t">
                            <div className="prose max-w-none">
                                {lecture.transcript || 'No transcript available for this lecture.'}
                            </div>
                        </div>
                    )}
                </div>

                {/* Notes Section */}
                <div className="bg-white mt-4 shadow-sm p-4 max-w-5xl mx-auto mb-8">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold">Your Notes</h2>
                        <div className="space-x-2">
                            {!isEditingNotes ? (
                                <button
                                    onClick={startEditingNotes}
                                    className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                                >
                                    Edit Notes
                                </button>
                            ) : (
                                <>
                                    <button
                                        onClick={saveNotes}
                                        className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                                    >
                                        Save
                                    </button>
                                    <button
                                        onClick={cancelEditingNotes}
                                        className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                                    >
                                        Cancel
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-2">
                        Take notes while watching the video. Click "Edit Notes" to make changes.
                    </p>
                    {isEditingNotes ? (
                        <textarea
                            value={tempNotes}
                            onChange={handleNotesChange}
                            className="w-full p-2 border rounded-md"
                            rows="6"
                            placeholder="Start typing your notes here..."
                        ></textarea>
                    ) : (
                        <div className="w-full p-2 border rounded-md bg-gray-50 min-h-[150px] whitespace-pre-wrap">
                            {notes || 'No notes yet. Click "Edit Notes" to start taking notes.'}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default LectureView; 