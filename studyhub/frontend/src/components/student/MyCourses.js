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

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <p className="text-zinc-600 dark:text-zinc-400">Loading courses...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center text-red-500 dark:text-red-400 p-4">
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">My Courses</h1>
                <div className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Search courses..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="px-4 py-2 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white placeholder-zinc-500 dark:placeholder-gray-400 border border-zinc-300 dark:border-zinc-600 focus:outline-none focus:border-blue-500"
                    />
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="px-4 py-2 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white border border-zinc-300 dark:border-zinc-600 focus:outline-none focus:border-blue-500"
                    >
                        <option value="all">All Courses</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses.map(course => (
                    <div key={course.id} className="bg-zinc-50 dark:bg-zinc-800 rounded-lg overflow-hidden hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors border border-zinc-200 dark:border-zinc-700">
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">{course.name}</h2>
                                    <p className="text-zinc-600 dark:text-gray-400 text-sm">{course.code}</p>
                                </div>
                                <span className={`px-2 py-1 text-xs rounded-full border ${
                                    course.is_active 
                                        ? 'bg-green-50 dark:bg-green-400/20 text-green-800 dark:text-green-400 border-green-200 dark:border-green-400/30' 
                                        : 'bg-zinc-100 dark:bg-gray-400/20 text-zinc-800 dark:text-gray-400 border-zinc-200 dark:border-gray-400/30'
                                }`}>
                                    {course.is_active ? 'Active' : 'Completed'}
                                </span>
                            </div>
                            <p className="text-zinc-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">{course.description}</p>
                            <div className="mb-4">
                                <div className="flex justify-between text-sm text-zinc-600 dark:text-gray-400 mb-1">
                                    <span>Progress</span>
                                    <span>0%</span>
                                </div>
                                <div className="w-full bg-zinc-200 dark:bg-zinc-600 rounded-full h-2">
                                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '0%' }}></div>
                                </div>
                            </div>
                            <div className="flex justify-between items-center text-sm text-zinc-600 dark:text-gray-400">
                                <button
                                    onClick={() => navigate(`/student/courses/${course.id}`)}
                                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                                >
                                    View Course →
                                </button>
                                <span>
                                    {course.start_date} - {course.end_date}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {filteredCourses.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-zinc-600 dark:text-gray-400">No courses found</p>
                </div>
            )}
        </div>
    );
};

export default MyCourses; 