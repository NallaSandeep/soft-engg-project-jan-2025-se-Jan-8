import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

const CourseDetail = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            const response = await courseApi.getCourseContent(courseId);
            if (response.success) {
                setCourse(response.data.data.course);
            } else {
                setError('Failed to load course content');
            }
        } catch (err) {
            setError('Failed to load course content');
            console.error('Error loading course content:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading course content...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 text-center">
                {error}
            </div>
        );
    }

    if (!course) {
        return (
            <div className="text-center py-8">
                <p className="text-gray-600">Course not found</p>
                <button
                    onClick={() => navigate('/student/courses')}
                    className="mt-4 text-blue-500 hover:text-blue-600"
                >
                    Return to Courses
                </button>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-6">
            {/* Course Header */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">{course.name}</h1>
                <p className="text-gray-600 mb-2">{course.code}</p>
                <p className="text-gray-700">{course.description}</p>
            </div>

            {/* Introduction Section */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h2 className="text-xl font-semibold mb-4">Introduction</h2>
                <p className="text-gray-700">
                    {course.introduction || 'Welcome to the course! Get started by exploring the course content below.'}
                </p>
            </div>

            {/* Weeks */}
            <div className="space-y-6">
                {course.weeks && course.weeks.length > 0 ? (
                    course.weeks.map(week => (
                        <div key={week.id} className="bg-white rounded-lg shadow">
                            <div className="p-6 border-b border-gray-200">
                                <h2 className="text-xl font-semibold">Week {week.number}: {week.title}</h2>
                                <p className="text-gray-600 mt-2">{week.description}</p>
                            </div>

                            {/* Lectures */}
                            {week.lectures && week.lectures.length > 0 && (
                                <div className="p-6 border-b border-gray-200">
                                    <h3 className="text-lg font-medium mb-4">Lectures</h3>
                                    <div className="space-y-3">
                                        {week.lectures.map(lecture => (
                                            <div
                                                key={lecture.id}
                                                onClick={() => navigate(`/student/courses/${courseId}/week/${week.id}/lecture/${lecture.id}`)}
                                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                                            >
                                                <div>
                                                    <h4 className="font-medium">{lecture.title}</h4>
                                                    <p className="text-sm text-gray-600">{lecture.description}</p>
                                                </div>
                                                <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                                </svg>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Assignments */}
                            {week.assignments && week.assignments.length > 0 && (
                                <div className="p-6">
                                    <h3 className="text-lg font-medium mb-4">Assignments</h3>
                                    <div className="space-y-3">
                                        {week.assignments.map(assignment => (
                                            <div
                                                key={assignment.id}
                                                onClick={() => navigate(`/student/assignments/${assignment.id}`)}
                                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                                            >
                                                <div>
                                                    <div className="flex items-center">
                                                        <h4 className="font-medium">{assignment.title}</h4>
                                                        <span className={`ml-3 px-2 py-1 text-xs rounded ${
                                                            assignment.type === 'practice'
                                                                ? 'bg-blue-100 text-blue-800'
                                                                : 'bg-green-100 text-green-800'
                                                        }`}>
                                                            {assignment.type === 'practice' ? 'Practice' : 'Graded'}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-gray-600">
                                                        Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                    </p>
                                                </div>
                                                <div className="flex items-center">
                                                    {assignment.completed && (
                                                        <span className="mr-3 text-green-600">
                                                            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                            </svg>
                                                        </span>
                                                    )}
                                                    <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                                                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                                    </svg>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <div className="text-center py-8 bg-white rounded-lg shadow">
                        <p className="text-gray-600">No content available for this course yet.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseDetail; 