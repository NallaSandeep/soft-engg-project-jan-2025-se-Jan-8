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
                <div className="text-gray-600">Loading dashboard...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 text-center p-4">{error}</div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold">Welcome, {user?.first_name}!</h1>
                    <p className="text-gray-600">Here's an overview of your courses and progress</p>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-2">Enrolled Courses</h3>
                    <p className="text-3xl font-bold text-blue-600">{courses.length}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-2">Pending Assignments</h3>
                    <p className="text-3xl font-bold text-yellow-600">0</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-2">Overall Progress</h3>
                    <p className="text-3xl font-bold text-green-600">0%</p>
                </div>
            </div>

            {/* Recent Courses */}
            <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                    <h2 className="text-xl font-semibold">My Courses</h2>
                </div>
                <div className="p-6">
                    {courses.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {courses.map(course => (
                                <div
                                    key={course.id}
                                    className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                                    onClick={() => navigate(`/courses/${course.id}`)}
                                >
                                    <h3 className="font-semibold mb-2">{course.name}</h3>
                                    <p className="text-sm text-gray-600 mb-4">{course.code}</p>
                                    <div className="flex justify-between text-sm">
                                        <span>Progress: 0%</span>
                                        <span>Assignments: {course.assignments?.length || 0}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <p className="text-gray-600 mb-4">You haven't enrolled in any courses yet.</p>
                            <button
                                onClick={() => navigate('/courses')}
                                className="text-blue-600 hover:text-blue-800"
                            >
                                Browse Available Courses →
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard; 