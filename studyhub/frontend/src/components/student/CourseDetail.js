import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { Card } from '../common/Card';

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
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading course content...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 dark:text-red-400 text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                {error}
            </div>
        );
    }

    if (!course) {
        return (
            <div className="text-center py-8">
                <p className="text-zinc-600 dark:text-zinc-400">Course not found</p>
                <button
                    onClick={() => navigate('/student/courses')}
                    className="mt-4 text-blue-500 dark:text-blue-400 hover:text-blue-600 dark:hover:text-blue-300"
                >
                    Return to Courses
                </button>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-6">
            {/* Course Header */}
            <Card className="p-6 mb-6 dark:bg-zinc-800">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">{course.name}</h1>
                <p className="text-zinc-600 dark:text-zinc-400 mb-2">{course.code}</p>
                <p className="text-zinc-700 dark:text-zinc-300">{course.description}</p>
            </Card>

            {/* Introduction Section */}
            <Card className="p-6 mb-6 dark:bg-zinc-800">
                <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Introduction</h2>
                <p className="text-zinc-700 dark:text-zinc-300">
                    {course.introduction || 'Welcome to the course! Get started by exploring the course content below.'}
                </p>
            </Card>

            {/* Weeks */}
            <div className="space-y-6">
                {course.weeks && course.weeks.length > 0 ? (
                    course.weeks.map(week => (
                        <Card key={week.id} className="dark:bg-zinc-800">
                            <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                                <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">Week {week.number}: {week.title}</h2>
                                <p className="text-zinc-600 dark:text-zinc-400 mt-2">{week.description}</p>
                            </div>

                            {/* Lectures */}
                            {week.lectures && week.lectures.length > 0 && (
                                <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                                    <h3 className="text-lg font-medium mb-4 text-zinc-900 dark:text-white">Lectures</h3>
                                    <div className="space-y-3">
                                        {week.lectures.map(lecture => (
                                            <div
                                                key={lecture.id}
                                                onClick={() => navigate(`/student/courses/${courseId}/week/${week.id}/lecture/${lecture.id}`)}
                                                className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-700 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-600 cursor-pointer transition-colors"
                                            >
                                                <div>
                                                    <h4 className="font-medium text-zinc-900 dark:text-white">{lecture.title}</h4>
                                                    <p className="text-sm text-zinc-600 dark:text-zinc-400">{lecture.description}</p>
                                                </div>
                                                <svg className="h-5 w-5 text-zinc-400 dark:text-zinc-500" viewBox="0 0 20 20" fill="currentColor">
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
                                    <h3 className="text-lg font-medium mb-4 text-zinc-900 dark:text-white">Assignments</h3>
                                    <div className="space-y-3">
                                        {week.assignments.map(assignment => (
                                            <div
                                                key={assignment.id}
                                                onClick={() => navigate(`/student/assignments/${assignment.id}`)}
                                                className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-700 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-600 cursor-pointer transition-colors"
                                            >
                                                <div>
                                                    <div className="flex items-center">
                                                        <h4 className="font-medium text-zinc-900 dark:text-white">{assignment.title}</h4>
                                                        <span className={`ml-3 px-2 py-1 text-xs rounded ${
                                                            assignment.type === 'practice'
                                                                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
                                                                : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                                                        }`}>
                                                            {assignment.type === 'practice' ? 'Practice' : 'Graded'}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                                        Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                    </p>
                                                </div>
                                                <div className="flex items-center">
                                                    {assignment.completed && (
                                                        <span className="mr-3 text-green-600 dark:text-green-500">
                                                            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                            </svg>
                                                        </span>
                                                    )}
                                                    <svg className="h-5 w-5 text-zinc-400 dark:text-zinc-500" viewBox="0 0 20 20" fill="currentColor">
                                                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                                    </svg>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </Card>
                    ))
                ) : (
                    <Card className="text-center py-8 dark:bg-zinc-800">
                        <p className="text-zinc-600 dark:text-zinc-400">No content available for this course yet.</p>
                    </Card>
                )}
            </div>
        </div>
    );
};

export default CourseDetail; 