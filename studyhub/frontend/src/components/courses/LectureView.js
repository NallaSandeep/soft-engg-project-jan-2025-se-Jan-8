import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { lectureApi } from '../../services/apiService';

const LectureView = () => {
    const { lectureId } = useParams();
    const [lecture, setLecture] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchLectureContent();
    }, [lectureId]);

    const fetchLectureContent = async () => {
        try {
            const response = await lectureApi.getLectureContent(lectureId);
            setLecture(response.data.data.lecture);
        } catch (err) {
            setError('Failed to load lecture content');
            console.error('Error loading lecture:', err);
        } finally {
            setLoading(false);
        }
    };

    const getYouTubeEmbedUrl = (url) => {
        const videoId = url.split('v=')[1];
        return `https://www.youtube.com/embed/${videoId}`;
    };

    if (loading) return <div>Loading lecture...</div>;
    if (error) return <div className="text-red-500">{error}</div>;
    if (!lecture) return <div>Lecture not found</div>;

    return (
        <div className="container mx-auto">
            <div className="bg-white rounded-lg shadow p-6">
                <h1 className="text-2xl font-bold mb-4">{lecture.title}</h1>
                
                {/* Video Player */}
                <div className="aspect-w-16 aspect-h-9 mb-6">
                    <iframe
                        src={getYouTubeEmbedUrl(lecture.youtube_url)}
                        title={lecture.title}
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        className="w-full h-[500px]"
                    />
                </div>

                {/* Description */}
                {lecture.description && (
                    <div className="mb-6">
                        <h2 className="text-xl font-semibold mb-2">Description</h2>
                        <p className="text-gray-700">{lecture.description}</p>
                    </div>
                )}

                {/* Transcript */}
                {lecture.transcript && (
                    <div>
                        <h2 className="text-xl font-semibold mb-2">Transcript</h2>
                        <div className="bg-gray-50 p-4 rounded">
                            <p className="text-gray-700 whitespace-pre-wrap">
                                {lecture.transcript}
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LectureView; 