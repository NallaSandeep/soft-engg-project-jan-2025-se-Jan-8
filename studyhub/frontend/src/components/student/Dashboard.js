import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';
import { Card } from '../common/Card';

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
            console.log('Fetching courses...');
            const response = await courseApi.getCourses();
            console.log('Courses response:', response);
            if (response.success) {
                setCourses(response.data || []);
            } else {
                setError(response.message || 'Failed to load courses');
            }
        } catch (err) {
            console.error('Error loading courses:', err);
            setError(err.message || 'Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading dashboard...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded relative" role="alert">
                <strong className="font-bold">Error!</strong>
                <span className="block sm:inline"> {error}</span>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Welcome, {user?.first_name}!</h1>
                    <p className="text-zinc-600 dark:text-zinc-400">Here's an overview of your courses and progress</p>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <Link to={`/${user?.role}/courses`}>
                <Card className="p-6 dark:bg-zinc-800">
                    <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">Enrolled Courses</h3>
                    <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{courses.length}</p>
                </Card>
                </Link>
                <Link to={`/${user?.role}/assignments`}>
                <Card className="p-6 dark:bg-zinc-800">
                    <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">Pending Assignments</h3>
                    <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">0</p>
                </Card>
                </Link>
                <Card className="p-6 dark:bg-zinc-800">
                    <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">Overall Progress</h3>
                    <p className="text-3xl font-bold text-green-600 dark:text-green-400">0%</p>
                </Card>
            </div>

            {/* Recent Courses */}
            <Card className="dark:bg-zinc-800">
                <div className="p-6 border-b dark:border-zinc-700">
                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">My Courses</h2>
                </div>
                <div className="p-6">
                    {courses.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {courses.map(course => (
                                <div
                                    key={course.id}
                                    className="border dark:border-zinc-700 rounded-lg p-4 hover:shadow-md dark:hover:shadow-zinc-900/50 transition-shadow cursor-pointer bg-white dark:bg-zinc-700"
                                    onClick={() => navigate(`/courses/${course.id}`)}
                                >
                                    <h3 className="font-semibold mb-2 text-zinc-900 dark:text-white">{course.name}</h3>
                                    <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">{course.code}</p>
                                    <div className="flex justify-between text-sm text-zinc-600 dark:text-zinc-400">
                                        <span>Progress: 0%</span>
                                        <span>Assignments: {course.assignments?.length || 0}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <p className="text-zinc-600 dark:text-zinc-400 mb-4">You haven't enrolled in any courses yet.</p>
                            <button
                                onClick={() => navigate('/courses')}
                                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                            >
                                Browse Available Courses →
                            </button>
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
};

export default StudentDashboard; 