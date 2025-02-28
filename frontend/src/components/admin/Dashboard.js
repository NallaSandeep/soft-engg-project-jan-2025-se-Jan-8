import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi, userApi, assignmentApi, adminApi } from '../../services/apiService';
import { formatDate } from '../../utils/dateUtils';

const DashboardCard = ({ title, value, description, onClick }) => (
    <div 
        className={`bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow ${onClick ? 'cursor-pointer' : ''}`}
        onClick={onClick}
    >
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <p className="text-3xl font-bold text-blue-600 my-2">{value}</p>
        <p className="text-sm text-gray-600">{description}</p>
    </div>
);

const AdminDashboard = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        totalCourses: 0,
        totalStudents: 0,
        totalAssignments: 0,
        totalQuestions: 0,
        recentCourses: [],
        recentAssignments: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const response = await adminApi.getDashboardStats();
            
            if (response.success) {
                const { stats, recentCourses, recentAssignments } = response.data;
                setStats({
                    totalCourses: stats.totalCourses,
                    totalStudents: stats.totalStudents,
                    totalAssignments: stats.totalAssignments,
                    totalQuestions: stats.totalQuestions,
                    recentCourses,
                    recentAssignments
                });
            } else {
                setError('Failed to load dashboard data');
            }
        } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setError('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading dashboard...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <DashboardCard
                    title="Total Courses"
                    value={stats.totalCourses}
                    description="Active courses in the platform"
                    onClick={() => navigate('/admin/courses')}
                />
                <DashboardCard
                    title="Total Students"
                    value={stats.totalStudents}
                    description="Enrolled students"
                    onClick={() => navigate('/admin/users')}
                />
                <DashboardCard
                    title="Total Assignments"
                    value={stats.totalAssignments}
                    description="Created assignments"
                    onClick={() => navigate('/admin/assignments')}
                />
                <DashboardCard
                    title="Question Bank"
                    value={stats.totalQuestions}
                    description="Available questions"
                    onClick={() => navigate('/admin/question-bank')}
                />
            </div>

            {/* Quick Actions */}
            <div className="mb-8">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <button
                        onClick={() => navigate('/admin/courses/new')}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                    >
                        Create Course
                    </button>
                    <button
                        onClick={() => navigate('/admin/assignments/new')}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                    >
                        Create Assignment
                    </button>
                    <button
                        onClick={() => navigate('/admin/question-bank/new')}
                        className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
                    >
                        Add Question
                    </button>
                    <button
                        onClick={() => navigate('/admin/users/new')}
                        className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
                    >
                        Add User
                    </button>
                    <button
                        onClick={() => navigate('/admin/users/enroll')}
                        className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700"
                    >
                        Enroll Students/TAs
                    </button>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Courses */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-800 mb-4">Recent Courses</h2>
                    <div className="space-y-4">
                        {stats.recentCourses.map(course => (
                            <div 
                                key={course.id}
                                className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                                onClick={() => navigate(`/admin/courses/${course.id}/content`)}
                            >
                                <div>
                                    <h3 className="font-medium">{course.name}</h3>
                                    <p className="text-sm text-gray-600">{course.code}</p>
                                </div>
                                <span className="text-sm text-gray-500">
                                    {new Date(course.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recent Assignments */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-800 mb-4">Recent Assignments</h2>
                    <div className="space-y-4">
                        {stats.recentAssignments.map(assignment => (
                            <div 
                                key={assignment.id}
                                className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                                onClick={() => navigate(`/admin/assignments/${assignment.id}`)}
                            >
                                <div>
                                    <h3 className="font-medium">{assignment.title}</h3>
                                    <p className="text-sm text-gray-600">Due: {new Date(assignment.due_date).toLocaleDateString()}</p>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-sm ${
                                    assignment.is_published 
                                        ? 'bg-green-100 text-green-800' 
                                        : 'bg-yellow-100 text-yellow-800'
                                }`}>
                                    {assignment.is_published ? 'Published' : 'Draft'}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;