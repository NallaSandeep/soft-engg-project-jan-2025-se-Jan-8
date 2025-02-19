import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';

const StudentDashboard = () => {
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
            const response = await courseApi.getCourses();
            if (response.success) {
                setCourses(response.data || []);
            } else {
                setError(response.message || 'Failed to load courses');
            }
        } catch (err) {
            setError(err.message || 'Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen bg-white dark:bg-gray-900">
                <div className="animate-pulse flex flex-col items-center">
                    <div className="w-12 h-12 border-4 border-gray-900 dark:border-white border-t-transparent rounded-full animate-spin"/>
                    <p className="mt-4 text-gray-600 dark:text-gray-400 font-medium">Loading your dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-white dark:bg-gray-900 flex items-center justify-center p-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-8 max-w-md w-full text-center">
                    <div className="text-red-500 dark:text-red-400 mb-4 text-lg font-medium">{error}</div>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-all duration-200"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white dark:bg-gray-900">
            <div className="container mx-auto px-4 py-8 space-y-8">
                <div className="bg-gray-50 dark:bg-gray-800 rounded-xl shadow-sm p-6">
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                        Welcome back, {user?.first_name}! 👋
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-2">Track your learning progress and manage your courses</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                        { title: 'Enrolled Courses', value: courses.length, color: 'text-gray-900 dark:text-white' },
                        { title: 'Pending Assignments', value: '0', color: 'text-gray-900 dark:text-white' },
                        { title: 'Overall Progress', value: '0%', color: 'text-gray-900 dark:text-white' }
                    ].map((stat, index) => (
                        <div key={index} className="bg-gray-50 dark:bg-gray-800 rounded-xl shadow-sm p-6 hover:shadow-md transition-all duration-300">
                            <h3 className="text-lg font-semibold mb-2 text-gray-600 dark:text-gray-400">{stat.title}</h3>
                            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                        </div>
                    ))}
                </div>

                <div className="bg-gray-50 dark:bg-gray-800 rounded-xl shadow-sm">
                    <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">My Courses</h2>
                        <button 
                            onClick={() => navigate('/courses')}
                            className="px-4 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-all duration-200"
                        >
                            Browse More
                        </button>
                    </div>
                    <div className="p-6">
                        {courses.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {courses.map(course => (
                                    <div
                                        key={course.id}
                                        onClick={() => navigate(`/courses/${course.id}`)}
                                        className="group bg-white dark:bg-gray-800 rounded-xl p-6 hover:shadow-md transition-all duration-300 cursor-pointer border border-gray-100 dark:border-gray-700"
                                    >
                                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors">
                                            {course.name}
                                        </h3>
                                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 mb-4">{course.code}</p>
                                        <div className="space-y-3">
                                            <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
                                                <span>Progress</span>
                                                <span>0%</span>
                                            </div>
                                            <div className="w-full h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                                                <div className="w-0 h-full bg-gray-900 dark:bg-white transition-all duration-500"/>
                                            </div>
                                            <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
                                                <span>Assignments</span>
                                                <span>{course.assignments?.length || 0}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12">
                                <div className="w-16 h-16 mx-auto mb-4 text-gray-400 dark:text-gray-500">
                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" 
                                              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                                    </svg>
                                </div>
                                <p className="text-gray-500 dark:text-gray-400 mb-6">Ready to start learning? Enroll in your first course!</p>
                                <button
                                    onClick={() => navigate('/courses')}
                                    className="px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-all duration-200"
                                >
                                    Browse Available Courses
                                </button>
                            </div>
                        )}
                    </div>    
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard;