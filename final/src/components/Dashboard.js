import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const placeholderCourses = [
    { id: 1, name: 'Introduction to Programming', code: 'CS101', description: 'Learn the basics of Python programming.', assignments: 3 },
    { id: 2, name: 'Data Structures & Algorithms', code: 'CS102', description: 'Understand fundamental data structures and algorithms.', assignments:0  },
    { id: 3, name: 'Introduction to ML', code: 'ML101', description: 'A beginner-friendly course on the fundamentals of Machine Learning, including supervised and unsupervised learning techniques.', assignments: 0 }
];

const Dashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    return (
        <div className="p-6 max-w-7xl mx-auto min-h-screen bg-gray-900 text-white">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-yellow-400">Welcome, {user?.first_name || user?.username}</h1>
                <p className="text-gray-400">Your learning dashboard</p>
            </div>

            {placeholderCourses.length === 0 ? (
                <div className="bg-gray-800 rounded-lg shadow-md p-6 text-center">
                    <p className="text-gray-400 mb-4">You haven't enrolled in any courses yet.</p>
                    <button
                        onClick={() => navigate('/courses')}
                        className="bg-yellow-500 text-gray-900 px-4 py-2 rounded font-semibold hover:bg-yellow-400"
                    >
                        Browse Available Courses
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {placeholderCourses.map(course => (
                        <div
                            key={course.id}
                            className="bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                            onClick={() => navigate(`/courses/${course.id}`)}
                        >
                            <div className="p-6">
                                <h2 className="text-xl font-semibold text-yellow-300 mb-2">{course.name}</h2>
                                <p className="text-gray-400 text-sm mb-4">{course.code}</p>
                                <p className="text-gray-300">{course.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
