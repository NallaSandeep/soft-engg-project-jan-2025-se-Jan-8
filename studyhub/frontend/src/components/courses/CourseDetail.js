import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { toast } from 'react-hot-toast';
import { Card } from '../common/Card';

const CourseDetail = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const [course, setCourse] = useState(null);
    const [weeks, setWeeks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    useEffect(() => {
        // Show success message if redirected from assignment submission
        if (location.state?.submissionSuccess) {
            const { score, maxScore } = location.state;
            toast.success(
                <div>
                    <p>Assignment submitted successfully!</p>
                    <p className="text-sm">Score: {score}/{maxScore}</p>
                </div>
            );
            // Clear the state to prevent showing the message again on refresh
            navigate(location.pathname, { replace: true });
        }
    }, [location.state]);

    const fetchCourseContent = async () => {
        try {
            const response = await courseApi.getCourseContent(courseId);
            const courseData = response.data.data.course;
            if (!courseData) {
                setError('Course not found');
                return;
            }
            setCourse(courseData);
            setWeeks(courseData.weeks || []);
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
                    onClick={() => navigate('/courses')}
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
                <h1 className="text-2xl font-bold mb-2 text-zinc-900 dark:text-white">{course.name}</h1>
                <p className="text-zinc-600 dark:text-zinc-400 mb-2">{course.code}</p>
                <p className="text-zinc-700 dark:text-zinc-300">{course.description}</p>
            </Card>

            {/* Course Content */}
            <div className="space-y-6">
                {weeks.length > 0 ? (
                    weeks.map(week => (
                        <Card key={week.id} className="p-6 dark:bg-zinc-800">
                            <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">
                                Week {week.number}: {week.title}
                            </h2>
                            <p className="text-zinc-700 dark:text-zinc-300 mb-4">{week.description}</p>

                            {/* Lectures */}
                            {week.lectures && week.lectures.length > 0 && (
                                <div className="mb-6">
                                    <h3 className="text-lg font-medium mb-3 text-zinc-900 dark:text-white">Lectures</h3>
                                    <div className="space-y-3">
                                        {week.lectures.map(lecture => (
                                            <div
                                                key={lecture.id}
                                                className="flex justify-between items-center p-3 bg-gray-50 dark:bg-zinc-700 rounded hover:bg-gray-100 dark:hover:bg-zinc-600 cursor-pointer transition-colors"
                                                onClick={() => navigate(`/lectures/${lecture.id}`)}
                                            >
                                                <div>
                                                    <h4 className="font-medium text-zinc-900 dark:text-white">{lecture.title}</h4>
                                                    <p className="text-sm text-zinc-600 dark:text-zinc-400">{lecture.description}</p>
                                                </div>
                                                <span className="text-blue-500 dark:text-blue-400">View Lecture →</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Assignments */}
                            {week.assignments && week.assignments.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-medium mb-3 text-zinc-900 dark:text-white">Assignments</h3>
                                    <div className="space-y-3">
                                        {week.assignments.map(assignment => (
                                            <div
                                                key={assignment.id}
                                                className="flex justify-between items-center p-3 bg-gray-50 dark:bg-zinc-700 rounded hover:bg-gray-100 dark:hover:bg-zinc-600 cursor-pointer transition-colors"
                                                onClick={() => navigate(`/assignments/${assignment.id}`)}
                                            >
                                                <div>
                                                    <h4 className="font-medium text-zinc-900 dark:text-white">{assignment.title}</h4>
                                                    <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                                        Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                    </p>
                                                </div>
                                                <span className="text-blue-500 dark:text-blue-400">Start Assignment →</span>
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