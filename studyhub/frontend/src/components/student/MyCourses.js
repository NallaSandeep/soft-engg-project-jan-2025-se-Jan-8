import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

const MyCourses = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('all'); // all, active, completed

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            setError(null);
            const response = await courseApi.getCourses();
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

    const filteredCourses = courses.filter(course => {
        const matchesSearch = course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            course.code.toLowerCase().includes(searchTerm.toLowerCase());
        
        if (filter === 'all') return matchesSearch;
        if (filter === 'active') return matchesSearch && course.is_active;
        if (filter === 'completed') return matchesSearch && !course.is_active;
        return matchesSearch;
    });

    if (loading) return <div className="flex justify-center items-center h-screen">Loading courses...</div>;
    if (error) return <div className="text-red-500 text-center p-4">{error}</div>;

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-2xl font-bold">My Courses</h1>
                <div className="flex space-x-4">
                    <input
                        type="text"
                        placeholder="Search courses..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="px-4 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-500 dark:bg-zinc-800 dark:text-gray-100"
                    />
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="px-8 py-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-500 dark:bg-zinc-800 dark:text-gray-100"
                    >
                        <option value="all">All Courses</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses.map(course => (
                    <div key={course.id} className="bg-gray-50 dark:bg-zinc-800 rounded-lg shadow-sm p-6">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-lg font-semibold">{course.name}</h2>
                                <p className="text-sm text-gray-600 dark:text-gray-400">{course.code}</p>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                                course.is_active 
                                    ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400' 
                                    : 'bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-400'
                            }`}>
                                {course.is_active ? 'Active' : 'Completed'}
                            </span>
                        </div>
                        <p className="text-gray-600 text-sm mb-4 line-clamp-2 dark:text-gray-400">{course.description}</p>
                        <div className="mb-4">
                            <div className="flex justify-between text-sm text-gray-600 mb-1 dark:text-gray-400">
                                <span>Progress</span>
                                <span>0%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                            </div>
                        </div>
                        <div className="flex justify-between items-center">
                            <button
                                onClick={() => navigate(`/courses/${course.id}`)}
                                className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                            >
                                View Course →
                            </button>
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                                {course.start_date} - {course.end_date}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            {filteredCourses.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-gray-600">No courses found</p>
                </div>
            )}
        </div>
    );
};

export default MyCourses; 