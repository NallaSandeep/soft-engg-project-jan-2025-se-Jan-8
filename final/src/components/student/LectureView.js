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

    if (!lecture) return <div className="text-center text-light mt-5">Lecture not found</div>;

    const videoId = getYouTubeVideoId(lecture.youtube_url);

    return (
        <div className="d-flex vh-100 bg-dark text-light">
            {/* Sidebar */}
            <div className="bg-black p-3 text-warning" style={{ width: "250px", overflowY: "auto" }}>
                <h4 className="mb-3">Course Content</h4>
                <button
                    className="btn btn-outline-warning w-100 text-start mb-2"
                    onClick={() => navigate('/courses')}
                >
                    ← Back to Course
                </button>
                <div className="mt-2">
                    {Object.keys(lectureData).map(id => (
                        <button
                            key={id}
                            onClick={() => navigate(`/courses/1/lectures/${id}`)}
                            className={`btn w-100 text-start mb-2 ${id === lectureId ? 'btn-warning' : 'btn-outline-warning'}`}
                        >
                            {lectureData[id].title}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-grow-1 p-4 overflow-auto">
                {/* Video Section */}
                <h2 className="text-warning">{lecture.title}</h2>
                <div className="ratio ratio-16x9 my-3">
                    <iframe
                        src={`https://www.youtube.com/embed/${videoId}`}
                        title={lecture.title}
                        allowFullScreen
                        className="rounded"
                    ></iframe>
                </div>

                {/* Transcript Section */}
                <div className="card bg-secondary text-light">
                    <div className="card-header d-flex justify-content-between">
                        <span>Lecture Transcript</span>
                        <button
                            onClick={() => setShowTranscript(!showTranscript)}
                            className="btn btn-sm btn-warning"
                        >
                            {showTranscript ? 'Hide' : 'Show'}
                        </button>
                    </div>
                    {showTranscript && (
                        <div className="card-body" style={{ whiteSpace: "pre-wrap" }}>
                            {lecture.transcript}
                        </div>
                    )}
                </div>

                {/* Notes Section */}
                <div className="card bg-secondary text-light mt-4">
                    <div className="card-header d-flex justify-content-between">
                        <span>Your Notes</span>
                        <div>
                            {!isEditingNotes ? (
                                <button onClick={startEditingNotes} className="btn btn-sm btn-warning">Edit</button>
                            ) : (
                                <>
                                    <button onClick={saveNotes} className="btn btn-sm btn-success me-2">Save</button>
                                    <button onClick={cancelEditingNotes} className="btn btn-sm btn-danger">Cancel</button>
                                </>
                            )}
                        </div>
                    </div>
                    <div className="card-body">
                        {isEditingNotes ? (
                            <textarea
                                value={tempNotes}
                                onChange={handleNotesChange}
                                className="form-control bg-dark text-light"
                                rows="5"
                                placeholder="Start typing your notes here..."
                            ></textarea>
                        ) : (
                            <div className="bg-dark p-3 rounded" style={{ minHeight: "100px" }}>
                                {notes || 'No notes yet. Click "Edit" to start taking notes.'}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LectureView;
