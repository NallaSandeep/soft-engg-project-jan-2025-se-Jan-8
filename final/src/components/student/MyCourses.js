import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Static course data for consistency
const coursesData = [
    { id: 1, name: "Intoduction to Programming", code: "CS101", description: "Introduction to ML concepts and algorithms.", is_active: true, start_date: "Jan 10, 2025", end_date: "Apr 30, 2025" },
    { id: 2, name: "Data Structures", code: "CS102", description: "Understanding processes, memory management, and scheduling.", is_active: true, start_date: "Aug 15, 2024", end_date: "Dec 10, 2024" },
    { id: 3, name: "Introduction to ML", code: "ML101", description: "Networking protocols, security, and communication models.", is_active: true, start_date: "Jan 15, 2025", end_date: "May 5, 2025" }
];

const MyCourses = () => {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('all'); // all, active, completed

    const filteredCourses = coursesData.filter(course => {
        const matchesSearch = course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            course.code.toLowerCase().includes(searchTerm.toLowerCase());
        
        if (filter === 'all') return matchesSearch;
        if (filter === 'active') return matchesSearch && course.is_active;
        if (filter === 'completed') return matchesSearch && !course.is_active;
        return matchesSearch;
    });

    return (
        <div className="container mx-auto px-4 py-8 text-gray-200">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-2xl font-bold text-yellow-400">My Courses</h1>
                <div className="flex space-x-4">
                    <input
                        type="text"
                        placeholder="Search courses..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="px-4 py-2 border border-yellow-400 bg-gray-900 text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
                    />
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="px-4 py-2 border border-yellow-400 bg-gray-900 text-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
                    >
                        <option value="all">All Courses</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses.map(course => (
                    <div key={course.id} className="bg-gray-800 rounded-lg shadow-md p-6 transition-transform transform hover:scale-105">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-lg font-semibold text-yellow-400">{course.name}</h2>
                                <p className="text-sm text-gray-400">{course.code}</p>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                                course.is_active 
                                    ? 'bg-green-500 text-gray-900' 
                                    : 'bg-gray-600 text-gray-200'
                            }`}>
                                {course.is_active ? 'Active' : 'Completed'}
                            </span>
                        </div>
                        <p className="text-gray-300 text-sm mb-4 line-clamp-2">{course.description}</p>
                        <div className="mb-4">
                            <div className="flex justify-between text-sm text-gray-400 mb-1">
                                <span>Progress</span>
                                <span>0%</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                                <div className="bg-yellow-400 h-2 rounded-full" style={{ width: '0%' }}></div>
                            </div>
                        </div>
                        <div className="flex justify-between items-center">
                            <button
                                onClick={() => navigate(`/courses/${course.id}`)}
                                className="text-yellow-400 hover:text-yellow-300 transition-colors"
                            >
                                View Course →
                            </button>
                            <span className="text-sm text-gray-400">
                                {course.start_date} - {course.end_date}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            {filteredCourses.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-gray-400">No courses found</p>
                </div>
            )}
        </div>
    );
};

export default MyCourses;
