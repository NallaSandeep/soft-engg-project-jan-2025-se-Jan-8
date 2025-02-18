import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const placeholderCourses = [
    { id: 1, name: 'Introduction to Programming', code: 'CS101', description: 'Learn the basics of Python programming.', assignments: 3 },
    { id: 2, name: 'Data Structures & Algorithms', code: 'CS102', description: 'Understand fundamental data structures and algorithms.', assignments:0  },
    { id: 3, name: 'Introduction to ML', code: 'ML101', description: 'A beginner-friendly course on the fundamentals of Machine Learning, including supervised and unsupervised learning techniques.', assignments: 0 }
];

const StudentDashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    return (
        <div className="p-6 max-w-7xl mx-auto min-h-screen bg-gray-900 text-white">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-yellow-400">Welcome, {user?.first_name || user?.username}!</h1>
                <p className="text-gray-400">Here's an overview of your courses and progress</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-gray-800 rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-semibold text-yellow-300 mb-2">Enrolled Courses</h3>
                    <p className="text-3xl font-bold text-yellow-400">{placeholderCourses.length}</p>
                </div>
                <div className="bg-gray-800 rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-semibold text-yellow-300 mb-2">Pending Assignments</h3>
                    <p className="text-3xl font-bold text-yellow-400">{placeholderCourses.reduce((acc, course) => acc + course.assignments, 0)}</p>
                </div>
                <div className="bg-gray-800 rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-semibold text-yellow-300 mb-2">Overall Progress</h3>
                    <p className="text-3xl font-bold text-yellow-400">0%</p>
                </div>
            </div>

            {/* My Courses */}
            <div className="bg-gray-800 rounded-lg shadow-md">
                <div className="p-6 border-b border-gray-700">
                    <h2 className="text-xl font-semibold text-yellow-300">My Courses</h2>
                </div>
                <div className="p-6">
                    {placeholderCourses.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {placeholderCourses.map(course => (
                                <div
                                    key={course.id}
                                    className="bg-gray-700 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
                                    onClick={() => navigate(`/courses/${course.id}`)}
                                >
                                    <h3 className="font-semibold text-yellow-400 mb-2">{course.name}</h3>
                                    <p className="text-sm text-gray-400 mb-4">{course.code}</p>
                                    <div className="flex justify-between text-sm text-gray-300">
                                        <span>Progress: 0%</span>
                                        <span>Assignments: {course.assignments}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8">
                            <p className="text-gray-400 mb-4">You haven't enrolled in any courses yet.</p>
                            <button
                                onClick={() => navigate('/courses')}
                                className="text-yellow-400 hover:text-yellow-300"
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
