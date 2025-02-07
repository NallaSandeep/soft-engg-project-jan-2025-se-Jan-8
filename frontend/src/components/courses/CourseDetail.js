import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { toast } from 'react-hot-toast';

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
                    onClick={() => navigate('/courses')}
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
                <h1 className="text-2xl font-bold mb-2">{course.name}</h1>
                <p className="text-gray-600 mb-2">{course.code}</p>
                <p className="text-gray-700">{course.description}</p>
            </div>

            {/* Course Content */}
            <div className="space-y-6">
                {weeks.length > 0 ? (
                    weeks.map(week => (
                        <div key={week.id} className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-xl font-semibold mb-4">
                                Week {week.number}: {week.title}
                            </h2>
                            <p className="text-gray-700 mb-4">{week.description}</p>

                            {/* Lectures */}
                            {week.lectures && week.lectures.length > 0 && (
                                <div className="mb-6">
                                    <h3 className="text-lg font-medium mb-3">Lectures</h3>
                                    <div className="space-y-3">
                                        {week.lectures.map(lecture => (
                                            <div
                                                key={lecture.id}
                                                className="flex justify-between items-center p-3 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer"
                                                onClick={() => navigate(`/lectures/${lecture.id}`)}
                                            >
                                                <div>
                                                    <h4 className="font-medium">{lecture.title}</h4>
                                                    <p className="text-sm text-gray-600">{lecture.description}</p>
                                                </div>
                                                <span className="text-blue-500">View Lecture →</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Assignments */}
                            {week.assignments && week.assignments.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-medium mb-3">Assignments</h3>
                                    <div className="space-y-3">
                                        {week.assignments.map(assignment => (
                                            <div
                                                key={assignment.id}
                                                className="flex justify-between items-center p-3 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer"
                                                onClick={() => navigate(`/assignments/${assignment.id}`)}
                                            >
                                                <div>
                                                    <h4 className="font-medium">{assignment.title}</h4>
                                                    <p className="text-sm text-gray-600">
                                                        Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                    </p>
                                                </div>
                                                <span className="text-blue-500">Start Assignment →</span>
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