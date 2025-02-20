import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const lectureData = {
    201: {
        title: "Lecture 1",
        youtube_url: "https://www.youtube.com/watch?v=aEPFZSzZ6VQ",
        transcript: `I quoted the example of driving a car the last week and this week I will continue quoting the 
same example. Now, because I did not find, I do not think there is a better example to explain how  
important it is for us to start learning, I mean start driving the car, start writing the program  
than simply keep looking at theory and syntax and then, lecture videos are very important. But  
once you understand what is what, you probably should move ahead, and then start coding.  
That is the first point I would like to tell you for the beginning of the second week and  
as you know, we tried (giving) making you warm up for programming and please note the things  
are not as simple as it appeared in week 1, things are going to get more complex and that  
is the very reason why we use the computer. Programming is all about doing complex things  
quickly and easily as I keep saying. So this week, we are going to see a few more top ups to  
programming skill set, which will be; firstly, we will tell you what one means by a variable...`
    },
    202: {
        title: "Lecture 2",
        youtube_url: "https://www.youtube.com/watch?v=XZSnqseRbZY",
        transcript: `Here is an important tip that I am going to convey through a small program. So let  
us start with this little story of two brothers, Ram and Lakshman. Let us say Ram's bank balance is  
one lakh and his bank loan, Ram's bank loan is let us say 5 lakhs.  
Lakshman, his brother's bank loan is, his brother's bank balance is let us say 20 lakhs  
and his bank loan is let us say 10 lakhs. Do you observe something here?  
Is it not indeed confusing to call it A, B, C and D? Is it not important that we make the  
variables sort of self-explanatory? And that we need not break our head on what exactly did I  
say just now? Was it bank balance or loan? Was it the brother Ram or the brother Lakshman?...`
    }
};

const LectureView = () => {
    const { lectureId } = useParams();
    const navigate = useNavigate();
    const [showTranscript, setShowTranscript] = useState(false);
    const [notes, setNotes] = useState('');
    const [isEditingNotes, setIsEditingNotes] = useState(false);
    const [tempNotes, setTempNotes] = useState('');

    const lecture = lectureData[lectureId];

    useEffect(() => {
        if (lecture) {
            const savedNotes = localStorage.getItem(`lecture-notes-${lectureId}`);
            if (savedNotes) {
                setNotes(savedNotes);
            }
        }
    }, [lectureId]);

    const handleNotesChange = (e) => setTempNotes(e.target.value);

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
        setIsEditingNotes(false);
    };

    const getYouTubeVideoId = (url) => {
        const match = url?.match(/(?:youtu\.be\/|v=|\/embed\/|\/v\/|watch\?v=)([^&\n?#]+)/);
        return match ? match[1] : null;
    };

    if (!lecture) {
        return (
            <div className="flex flex-col items-center justify-center h-screen bg-zinc-50 dark:bg-zinc-900">
                <div className="text-zinc-900 dark:text-white mb-4">Lecture not found</div>
                <button
                    onClick={() => navigate('/courses')}
                    className="px-4 py-2 text-sm font-medium rounded-lg
                             bg-zinc-900 dark:bg-white 
                             text-white dark:text-zinc-900
                             hover:bg-zinc-800 dark:hover:bg-zinc-100
                             transition-colors duration-200"
                >
                    Return to Course
                </button>
            </div>
        );
    }

    const videoId = getYouTubeVideoId(lecture.youtube_url);
    return (
        <div className="flex h-screen bg-zinc-50 dark:bg-zinc-900">
            {/* Sidebar */}
            <div className="w-72 bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm overflow-y-auto">
                <div className="p-6">
                    <button
                        onClick={() => navigate('/courses')}
                        className="text-sm font-medium text-zinc-900 dark:text-white
                                 hover:text-zinc-600 dark:hover:text-zinc-400
                                 transition-colors flex items-center gap-2"
                    >
                        ← Back to Course
                    </button>
                </div>
                <nav className="p-4 space-y-2">
                    {Object.keys(lectureData).map(id => (
                        <button
                            key={id}
                            onClick={() => navigate(`/courses/1/lectures/${id}`)}
                            className={`w-full text-left px-4 py-2 rounded-lg text-sm font-medium 
                                      transition-colors ${id === lectureId 
                                ? 'bg-zinc-900 text-zinc-100 dark:bg-white dark:text-zinc-900'
                                : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-700/50'
                            }`}
                        >
                            {lectureData[id].title}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-y-auto p-6 bg-zinc-100 dark:bg-zinc-900">
                <div className="max-w-4xl mx-auto space-y-6">
                    {/* Video Section */}
                    <div className="relative mb-6">
                        <div className="relative z-10">
                            <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-6">
                                {lecture.title}
                            </h1>
                            <div className="w-full max-w-3xl mx-auto">
                                <div className="relative" style={{ paddingBottom: '56.25%' }}>
                                    <iframe
                                        src={`https://www.youtube.com/embed/${videoId}`}
                                        title={lecture.title}
                                        allowFullScreen
                                        className="absolute top-0 left-0 w-full h-full rounded-lg
                                                 bg-zinc-200 dark:bg-zinc-800"
                                    ></iframe>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Transcript Section */}
                    <div className="bg-white/80 dark:bg-zinc-800/80 rounded-xl backdrop-blur-sm">
                        <div className="flex items-center justify-between p-4">
                            <span className="font-medium text-zinc-900 dark:text-white">
                                Lecture Transcript
                            </span>
                            <button
                                onClick={() => setShowTranscript(!showTranscript)}
                                className="px-3 py-1 text-sm font-medium rounded-lg
                                         bg-zinc-900 dark:bg-white 
                                         text-zinc-100 dark:text-zinc-900
                                         hover:bg-zinc-800 dark:hover:bg-zinc-100
                                         transition-colors"
                            >
                                {showTranscript ? 'Hide' : 'Show'}
                            </button>
                        </div>
                        {showTranscript && (
                            <div className="p-4 text-zinc-600 dark:text-zinc-400 
                                          bg-zinc-50/50 dark:bg-zinc-900/50 rounded-b-xl" 
                                 style={{ whiteSpace: "pre-wrap" }}>
                                {lecture.transcript}
                            </div>
                        )}
                    </div>

                    {/* Notes Section */}
                    <div className="bg-white/80 dark:bg-zinc-800/80 rounded-xl backdrop-blur-sm">
                        <div className="flex items-center justify-between p-4">
                            <span className="font-medium text-zinc-900 dark:text-white">
                                Your Notes
                            </span>
                            <div className="space-x-2">
                                {!isEditingNotes ? (
                                    <button 
                                        onClick={startEditingNotes}
                                        className="px-3 py-1 text-sm font-medium rounded-lg
                                                 bg-zinc-900 dark:bg-white 
                                                 text-zinc-100 dark:text-zinc-900
                                                 hover:bg-zinc-800 dark:hover:bg-zinc-100
                                                 transition-colors"
                                    >
                                        Edit
                                    </button>
                                ) : (
                                    <>
                                        <button 
                                            onClick={saveNotes}
                                            className="px-3 py-1 text-sm font-medium rounded-lg
                                                     bg-emerald-600 text-zinc-100
                                                     hover:bg-emerald-700
                                                     transition-colors"
                                        >
                                            Save
                                        </button>
                                        <button 
                                            onClick={cancelEditingNotes}
                                            className="px-3 py-1 text-sm font-medium rounded-lg
                                                     bg-zinc-200 dark:bg-zinc-700
                                                     text-zinc-900 dark:text-white
                                                     hover:bg-zinc-300 dark:hover:bg-zinc-600
                                                     transition-colors"
                                        >
                                            Cancel
                                        </button>
                                    </>
                                )}
                            </div>
                        </div>
                        <div className="p-4">
                            {isEditingNotes ? (
                                <textarea
                                    value={tempNotes}
                                    onChange={handleNotesChange}
                                    className="w-full min-h-[200px] p-3 rounded-lg
                                             bg-zinc-50 dark:bg-zinc-900
                                             text-zinc-900 dark:text-white
                                             focus:outline-none focus:ring-2 
                                             focus:ring-zinc-500/50 dark:focus:ring-zinc-400/50
                                             placeholder-zinc-400 dark:placeholder-zinc-600"
                                    placeholder="Start typing your notes here..."
                                />
                            ) : (
                                <div className="min-h-[200px] p-3 rounded-lg
                                              bg-zinc-50 dark:bg-zinc-900
                                              text-zinc-600 dark:text-zinc-400">
                                    {notes || 'No notes yet. Click "Edit" to start taking notes.'}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LectureView;