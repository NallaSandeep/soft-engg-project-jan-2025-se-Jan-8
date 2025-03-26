import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { Card } from '../common/Card';

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
                // Fetch progress for each course
                const coursesWithProgress = await Promise.all(
                    response.data.map(async (course) => {
                        const progressResponse = await courseApi.getCourseProgress(course.id);
                        return {
                            ...course,
                            progress: progressResponse.success ? progressResponse.data : { percentage: 0, completed_items: 0, total_items: 0 }
                        };
                    })
                );
                setCourses(coursesWithProgress);
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
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading courses...</span>
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
                        className="px-4 py-2 rounded-lg bg-zinc-50 dark:bg-zinc-800 text-zinc-900 dark:text-white placeholder-zinc-500 dark:placeholder-zinc-400 border border-zinc-200 dark:border-zinc-700 focus:outline-none focus:border-blue-500"
                    />
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="px-4 py-2 rounded-lg bg-zinc-50 dark:bg-zinc-800 text-zinc-900 dark:text-white border border-zinc-200 dark:border-zinc-700 focus:outline-none focus:border-blue-500"
                    >
                        <option value="all">All Courses</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
            </div>

            {error && (
                <div className="text-red-500 dark:text-red-400 text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg mb-6">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses.map(course => (
                    <Card key={course.id} className="overflow-hidden hover:bg-zinc-50 dark:hover:bg-zinc-700/50 transition-colors cursor-pointer">
                        <div className="p-6" onClick={() => navigate(`/student/courses/${course.id}`)}>
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">{course.name}</h2>
                                    <p className="text-zinc-600 dark:text-zinc-400 text-sm">{course.code}</p>
                                </div>
                                <span className={`px-2 py-1 text-xs rounded-full ${
                                    course.is_active 
                                        ? 'bg-green-50 dark:bg-green-400/20 text-green-800 dark:text-green-400 border border-green-200 dark:border-green-400/30' 
                                        : 'bg-zinc-100 dark:bg-zinc-400/20 text-zinc-800 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-400/30'
                                }`}>
                                    {course.is_active ? 'Active' : 'Completed'}
                                </span>
                            </div>
                            
                            <p className="text-zinc-600 dark:text-zinc-400 text-sm mb-4 line-clamp-2">{course.description}</p>
                            
                            {/* Progress Section */}
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm text-zinc-600 dark:text-zinc-400">
                                    <span>Progress</span>
                                    <span>{course.progress?.percentage || 0}%</span>
                                </div>
                                <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-2">
                                    <div 
                                        className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                                        style={{ width: `${course.progress?.percentage || 0}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-xs text-zinc-500 dark:text-zinc-400">
                                    <span>{course.progress?.completed_items || 0} of {course.progress?.total_items || 0} items completed</span>
                                </div>
                            </div>

                            <div className="flex justify-between items-center mt-4 text-sm">
                                <span className="text-zinc-600 dark:text-zinc-400">
                                    {new Date(course.start_date).toLocaleDateString()} - {new Date(course.end_date).toLocaleDateString()}
                                </span>
                                <button
                                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
                                >
                                    View Course →
                                </button>
                            </div>
                        </div>
                    </Card>
                ))}
            </div>

            {filteredCourses.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-zinc-600 dark:text-zinc-400">
                        {searchTerm ? 'No courses match your search' : 'No courses available'}
                    </p>
                </div>
            )}
        </div>
    );
};

export default MyCourses; 