import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';

const Dashboard = () => {
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
            setCourses(response.data.data.courses || []);
        } catch (err) {
            setError('Failed to load courses');
            console.error('Error loading courses:', err);
        } finally {
            setLoading(false);
        }
    };

    const renderStudentDashboard = () => (
        <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">My Courses</h2>
                {courses.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {courses.map(course => (
                            <div
                                key={course.id}
                                className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                                onClick={() => navigate(`/courses/${course.id}`)}
                            >
                                <h3 className="font-medium mb-2">{course.name}</h3>
                                <p className="text-sm text-gray-600 mb-4">{course.code}</p>
                                <div className="flex justify-between text-sm text-gray-500">
                                    <span>{course.weeks?.length || 0} weeks</span>
                                    <span>{course.lectures?.length || 0} lectures</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <p className="text-gray-600 mb-4">You haven't enrolled in any courses yet.</p>
                        <button
                            onClick={() => navigate('/courses')}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                        >
                            Browse Courses
                        </button>
                    </div>
                )}
            </div>
        </div>
    );

    const renderAdminDashboard = () => (
        <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button
                        onClick={() => navigate('/course-management')}
                        className="p-4 bg-blue-50 rounded-lg hover:bg-blue-100"
                    >
                        <h3 className="font-medium mb-2">Manage Courses</h3>
                        <p className="text-sm text-gray-600">Create and manage course content</p>
                    </button>
                    <button
                        onClick={() => navigate('/courses')}
                        className="p-4 bg-green-50 rounded-lg hover:bg-green-100"
                    >
                        <h3 className="font-medium mb-2">View All Courses</h3>
                        <p className="text-sm text-gray-600">Browse all available courses</p>
                    </button>
                </div>
            </div>

            {courses.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-semibold mb-4">Recent Courses</h2>
                    <div className="space-y-4">
                        {courses.slice(0, 3).map(course => (
                            <div
                                key={course.id}
                                className="flex justify-between items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                                onClick={() => navigate(`/course-management/${course.id}/content`)}
                            >
                                <div>
                                    <h3 className="font-medium">{course.name}</h3>
                                    <p className="text-sm text-gray-600">{course.code}</p>
                                </div>
                                <span className="text-blue-500">Manage →</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );

    if (loading) return (
        <div className="flex justify-center items-center h-full">
            <div className="text-gray-600">Loading dashboard...</div>
        </div>
    );

    if (error) return (
        <div className="text-red-500 text-center">
            {error}
        </div>
    );

    return (
        <div className="container mx-auto px-4 py-6">
            <h1 className="text-2xl font-bold mb-6">Welcome, {user?.username}!</h1>
            {user?.role === 'admin' || user?.role === 'teacher' ? renderAdminDashboard() : renderStudentDashboard()}
        </div>
    );
};

export default Dashboard; 