import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../services/apiService';
import { useAuth } from '../hooks/useAuth';

const Dashboard = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { user } = useAuth();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            setError('');
            
            const response = await courseApi.getCourses();
            if (response.success && response.data) {
                setCourses(response.data);
            } else {
                setError('No courses available');
            }
        } catch (err) {
            console.error('Dashboard error:', err);
            setError('Failed to fetch courses');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="text-gray-600">Loading courses...</div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Welcome, {user?.first_name || user?.username}</h1>
                <p className="text-gray-600">Your learning dashboard</p>
            </div>

            {error ? (
                <div className="bg-white rounded-lg shadow p-6 text-center">
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={() => navigate('/courses')}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                        Browse Available Courses
                    </button>
                </div>
            ) : courses.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-6 text-center">
                    <p className="text-gray-600 mb-4">You haven't enrolled in any courses yet.</p>
                    <button
                        onClick={() => navigate('/courses')}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                        Browse Available Courses
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {courses.map(course => (
                        <div
                            key={course.id}
                            className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
                            onClick={() => navigate(`/courses/${course.id}`)}
                        >
                            <div className="p-6">
                                <h2 className="text-xl font-semibold text-gray-900 mb-2">{course.name}</h2>
                                <p className="text-gray-600 text-sm mb-4">{course.code}</p>
                                <p className="text-gray-500">{course.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard; 