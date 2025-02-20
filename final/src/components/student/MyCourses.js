import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const coursesData = [
    { id: 1, name: "Introduction to Programming", code: "CS101", description: "Introduction to ML concepts and algorithms.", is_active: true, start_date: "Jan 10, 2025", end_date: "Apr 30, 2025" },
    { id: 2, name: "Data Structures", code: "CS102", description: "Understanding processes, memory management, and scheduling.", is_active: true, start_date: "Aug 15, 2024", end_date: "Dec 10, 2024" },
    { id: 3, name: "Introduction to ML", code: "ML101", description: "Networking protocols, security, and communication models.", is_active: true, start_date: "Jan 15, 2025", end_date: "May 5, 2025" }
];

const MyCourses = () => {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('all');

    const filteredCourses = coursesData.filter(course => {
        const matchesSearch = course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            course.code.toLowerCase().includes(searchTerm.toLowerCase());
        
        if (filter === 'all') return matchesSearch;
        if (filter === 'active') return matchesSearch && course.is_active;
        if (filter === 'completed') return matchesSearch && !course.is_active;
        return matchesSearch;
    });

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">My Courses</h1>
                <div className="flex flex-col sm:flex-row gap-4">
                    <input
                        type="text"
                        placeholder="Search courses..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="px-4 py-2 text-sm bg-white/60 dark:bg-zinc-800/60 
                                 text-zinc-900 dark:text-white rounded-lg
                                 border border-zinc-200/50 dark:border-zinc-700/50
                                 focus:outline-none focus:ring-2 focus:ring-zinc-500/50 dark:focus:ring-zinc-400/50
                                 placeholder:text-zinc-400 dark:placeholder:text-zinc-500
                                 hover:bg-white dark:hover:bg-zinc-800 transition-all duration-200"
                    />
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="px-4 py-2 text-sm bg-white/60 dark:bg-zinc-800/60 
                                 text-zinc-900 dark:text-white rounded-lg
                                 border border-zinc-200/50 dark:border-zinc-700/50
                                 focus:outline-none focus:ring-2 focus:ring-zinc-500/50 dark:focus:ring-zinc-400/50
                                 hover:bg-white dark:hover:bg-zinc-800 transition-all duration-200"
                    >
                        <option value="all">All Courses</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
            </div>

            {/* Course Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses.map(course => (
                    <div 
                        key={course.id} 
                        className="group bg-white/80 dark:bg-zinc-800/80 rounded-xl p-6 
                                 backdrop-blur-sm transition-all duration-200
                                 hover:bg-white dark:hover:bg-zinc-800
                                 shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                 dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]
                                 hover:shadow-[0_4px_12px_-4px_rgba(0,0,0,0.1)]
                                 dark:hover:shadow-[0_4px_12px_-4px_rgba(0,0,0,0.4)]"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">{course.name}</h2>
                                <p className="text-sm text-zinc-500 dark:text-zinc-400">{course.code}</p>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded-full transition-colors
                                ${course.is_active 
                                    ? 'bg-zinc-900/90 text-zinc-100 dark:bg-white/90 dark:text-zinc-900' 
                                    : 'bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300'
                                }`}>
                                {course.is_active ? 'Active' : 'Completed'}
                            </span>
                        </div>
                        <p className="text-zinc-600 dark:text-zinc-300 text-sm mb-4 line-clamp-2">
                            {course.description}
                        </p>
                        <div className="mb-4">
                            <div className="flex justify-between text-sm text-zinc-500 dark:text-zinc-400 mb-1">
                                <span>Progress</span>
                                <span>0%</span>
                            </div>
                            <div className="w-full bg-zinc-100 dark:bg-zinc-700/50 rounded-full h-2 overflow-hidden">
                                <div className="bg-zinc-900/90 dark:bg-white/90 h-2 rounded-full 
                                            transition-all duration-500 ease-in-out" 
                                     style={{ width: '0%' }}>
                                </div>
                            </div>
                        </div>
                        <div className="flex justify-between items-center">
                            <button
                                onClick={() => navigate(`/courses/${course.id}`)}
                                className="text-zinc-900 dark:text-white group-hover:text-zinc-600 
                                         dark:group-hover:text-zinc-300 transition-colors
                                         text-sm font-medium inline-flex items-center"
                            >
                                View Course
                                <span className="ml-1 group-hover:translate-x-0.5 transition-transform">→</span>
                            </button>
                            <span className="text-sm text-zinc-500 dark:text-zinc-400">
                                {course.start_date} - {course.end_date}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Empty State */}
            {filteredCourses.length === 0 && (
                <div className="text-center py-12 bg-white/80 dark:bg-zinc-800/80 rounded-xl
                              backdrop-blur-sm">
                    <p className="text-zinc-500 dark:text-zinc-400">
                        No courses found
                    </p>
                </div>
            )}
        </div>
    );
};

export default MyCourses;