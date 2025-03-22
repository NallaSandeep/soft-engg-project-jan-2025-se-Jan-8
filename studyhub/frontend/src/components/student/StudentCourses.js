import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

const StudentCourses = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchCourses = async () => {
            try {
                setLoading(true);
                const response = await courseApi.getCourses();
                setCourses(Array.isArray(response.data) ? response.data : []);
            } catch (err) {
                console.error('Error fetching courses:', err);
                setError('Failed to load courses');
            } finally {
                setLoading(false);
            }
        };

        fetchCourses();
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <p className="text-gray-400">Loading courses...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center text-red-400 p-4">
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-white">My Courses</h1>
                <div className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Search courses..."
                        className="px-4 py-2 rounded-lg bg-zinc-700 text-white placeholder-gray-400 border border-zinc-600 focus:outline-none focus:border-blue-500"
                    />
                    <select className="px-4 py-2 rounded-lg bg-zinc-700 text-white border border-zinc-600 focus:outline-none focus:border-blue-500">
                        <option value="">All</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="upcoming">Upcoming</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {courses.map(course => (
                    <div
                        key={course.code}
                        className="bg-zinc-800 rounded-lg overflow-hidden hover:bg-zinc-700 transition-colors cursor-pointer"
                    >
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h2 className="text-xl font-semibold text-white mb-2">{course.name}</h2>
                                    <p className="text-gray-400 text-sm">{course.code}</p>
                                </div>
                                <span className="px-2 py-1 text-xs rounded-full bg-green-400/20 text-green-400">
                                    Active
                                </span>
                            </div>
                            <p className="text-gray-400 mb-4 line-clamp-2">{course.description}</p>
                            <div className="flex justify-between items-center text-sm text-gray-400">
                                <div>Progress: {course.progress || 0}%</div>
                                <div>{course.start_date} - {course.end_date}</div>
                            </div>
                            <button
                                onClick={() => navigate(`/student/course/${course.code}`)}
                                className="mt-4 w-full text-center px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                            >
                                View Course →
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StudentCourses; 