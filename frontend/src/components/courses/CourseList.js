import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';

const CourseList = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const { user } = useAuth();

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getCourses();
            setCourses(response || []);
        } catch (err) {
            setError('Failed to load courses');
            console.error('Error loading courses:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleEnroll = async (courseId) => {
        try {
            await courseApi.enrollStudent(courseId, user.id);
            // Refresh course list after enrollment
            fetchCourses();
        } catch (err) {
            setError('Failed to enroll in course');
            console.error('Error enrolling in course:', err);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading courses...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 text-center p-4">
                {error}
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">
                        {user?.role === 'admin' ? 'Course Management' : 'Your Courses'}
                    </h1>
                    <p className="text-gray-600">
                        {user?.role === 'admin' 
                            ? 'Manage and oversee all courses on the platform'
                            : `Welcome, ${user?.first_name}`}
                    </p>
                </div>
                {user?.role === 'admin' && (
                    <button
                        onClick={() => navigate('/admin/courses/new')}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Create New Course
                    </button>
                )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {courses.length > 0 ? (
                    courses.map(course => (
                        <div key={course.id} className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-xl font-semibold mb-2">{course.name}</h2>
                            <p className="text-gray-600 mb-2">{course.code}</p>
                            <p className="text-gray-700 mb-4">{course.description}</p>
                            
                            <div className="flex flex-col space-y-2">
                                {user?.role === 'admin' ? (
                                    <>
                                        <button
                                            onClick={() => navigate(`/admin/courses/${course.id}/edit`)}
                                            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                                        >
                                            Edit Course
                                        </button>
                                        <button
                                            onClick={() => navigate(`/admin/courses/${course.id}/students`)}
                                            className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                                        >
                                            Manage Students
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        <button
                                            onClick={() => navigate(`/courses/${course.id}`)}
                                            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                                        >
                                            View Course
                                        </button>
                                        {user?.role === 'student' && (
                                            <button
                                                onClick={() => handleEnroll(course.id)}
                                                className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                                            >
                                                Enroll Now
                                            </button>
                                        )}
                                    </>
                                )}
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="col-span-full text-center py-8 bg-white rounded-lg shadow">
                        <p className="text-gray-600">No courses found.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseList; 