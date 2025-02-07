import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import ReactMarkdown from 'react-markdown';

const CourseView = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeSection, setActiveSection] = useState('introduction');

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            setError(null);
            const response = await courseApi.getCourseContent(courseId);
            if (response.success) {
                setCourse(response.data);
            } else {
                setError(response.message || 'Failed to load course content');
            }
        } catch (err) {
            console.error('Error loading course content:', err);
            setError(err.message || 'Failed to load course content');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="flex justify-center items-center h-screen">Loading course content...</div>;
    if (error) return <div className="text-red-500 text-center p-4">{error}</div>;
    if (!course) return <div className="text-center p-4">Course not found</div>;

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Left Sidebar - Course Structure */}
            <div className="w-64 bg-white shadow-lg overflow-y-auto">
                <div className="p-4 border-b">
                    <h2 className="text-lg font-semibold">{course.code}</h2>
                    <p className="text-sm text-gray-600">{course.name}</p>
                </div>
                <nav className="p-2">
                    <button
                        onClick={() => setActiveSection('introduction')}
                        className={`w-full text-left p-2 rounded ${
                            activeSection === 'introduction' ? 'bg-blue-50 text-blue-600' : 'hover:bg-gray-50'
                        }`}
                    >
                        Course Introduction
                    </button>
                    
                    {course.weeks?.map(week => (
                        <div key={week.id} className="mb-2">
                            <div className="p-2 bg-gray-50 font-medium">
                                Week {week.number}: {week.title}
                            </div>
                            {week.lectures?.map(lecture => (
                                <button
                                    key={lecture.id}
                                    onClick={() => navigate(`/courses/${courseId}/lectures/${lecture.id}`)}
                                    className="w-full text-left p-2 pl-6 text-sm hover:bg-gray-50"
                                >
                                    {lecture.title}
                                </button>
                            ))}
                            {week.assignments?.map(assignment => (
                                <button
                                    key={assignment.id}
                                    onClick={() => navigate(`/courses/${courseId}/assignments/${assignment.id}`)}
                                    className="w-full text-left p-2 pl-6 text-sm text-green-600 hover:bg-gray-50"
                                >
                                    📝 {assignment.title}
                                </button>
                            ))}
                        </div>
                    ))}
                </nav>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto p-6">
                {activeSection === 'introduction' ? (
                    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-sm p-6">
                        <h1 className="text-3xl font-bold mb-4">{course.name}</h1>
                        <div className="mb-6">
                            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                                {course.code}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-6 mb-8">
                            <div>
                                <h3 className="text-lg font-semibold mb-2">Course Faculty</h3>
                                <p className="text-gray-600">{course.created_by}</p>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold mb-2">Course Duration</h3>
                                <p className="text-gray-600">
                                    {course.start_date} - {course.end_date}
                                </p>
                            </div>
                        </div>

                        <div className="prose max-w-none">
                            <h2 className="text-xl font-semibold mb-4">Course Description</h2>
                            <ReactMarkdown>{course.description}</ReactMarkdown>
                        </div>

                        <div className="mt-8">
                            <h2 className="text-xl font-semibold mb-4">Course Structure</h2>
                            <div className="space-y-4">
                                {course.weeks?.map(week => (
                                    <div key={week.id} className="border rounded-lg p-4">
                                        <h3 className="font-medium mb-2">
                                            Week {week.number}: {week.title}
                                        </h3>
                                        <p className="text-gray-600 text-sm mb-2">{week.description}</p>
                                        <div className="pl-4">
                                            {week.lectures?.map(lecture => (
                                                <div key={lecture.id} className="text-sm py-1">
                                                    • {lecture.title}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : null}
            </div>
        </div>
    );
};

export default CourseView; 