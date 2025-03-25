import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../services/apiService';
import { useAuth } from '../hooks/useAuth';
import { Card } from './common/Card';

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
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading courses...</span>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Welcome, {user?.first_name || user?.username}</h1>
                <p className="text-zinc-600 dark:text-zinc-400">Your learning dashboard</p>
            </div>

            {error ? (
                <Card className="p-6 text-center dark:bg-zinc-800">
                    <p className="text-zinc-600 dark:text-zinc-400 mb-4">{error}</p>
                    <button
                        onClick={() => navigate('/courses')}
                        className="bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 text-white px-4 py-2 rounded"
                    >
                        Browse Available Courses
                    </button>
                </Card>
            ) : courses.length === 0 ? (
                <Card className="p-6 text-center dark:bg-zinc-800">
                    <p className="text-zinc-600 dark:text-zinc-400 mb-4">You haven't enrolled in any courses yet.</p>
                    <button
                        onClick={() => navigate('/courses')}
                        className="bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 text-white px-4 py-2 rounded"
                    >
                        Browse Available Courses
                    </button>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {courses.map(course => (
                        <Card
                            key={course.id}
                            className="hover:shadow-lg dark:hover:shadow-zinc-900/50 transition-shadow cursor-pointer dark:bg-zinc-800"
                            onClick={() => navigate(`/student/courses/${course.id}`)}
                        >
                            <div className="p-6">
                                <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">{course.name}</h2>
                                <p className="text-zinc-600 dark:text-zinc-400 text-sm mb-4">{course.code}</p>
                                <p className="text-zinc-500 dark:text-zinc-500">{course.description}</p>
                                <button
                                    key={course.id}
                                    onClick={() => navigate(`/student/courses/${course.id}`)}
                                    className="text-blue-600 hover:text-blue-800"
                                >
                                    View Course →
                                </button>
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard; 