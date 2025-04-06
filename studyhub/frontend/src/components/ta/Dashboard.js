import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi, userApi, assignmentApi, taApi } from '../../services/apiService';
import { formatDate } from '../../utils/dateUtils';
import { 
    PlusCircleIcon,
    AcademicCapIcon,
    UserGroupIcon,
    ClipboardDocumentListIcon,
    QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';

const DashboardCard = ({ title, value, description, icon: Icon, onClick }) => (
    <div 
        className={`glass-card p-6 hover:shadow-lg transition-shadow ${onClick ? 'cursor-pointer' : ''}`}
        onClick={onClick}
    >
        <div className="flex justify-between items-start">
            <div>
                <h3 className="text-lg font-semibold text-zinc-900 dark:text-white">{title}</h3>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 my-2">{value}</p>
                <p className="text-sm text-zinc-600 dark:text-zinc-400">{description}</p>
            </div>
            {Icon && <Icon className="w-8 h-8 text-zinc-400 dark:text-zinc-500" />}
        </div>
    </div>
);

const ActionButton = ({ label, icon: Icon, onClick, color = 'blue' }) => {
    const colorClasses = {
        blue: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white',
        green: 'bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-700 dark:hover:bg-emerald-600 text-white',
        purple: 'bg-purple-600 hover:bg-purple-700 dark:bg-purple-700 dark:hover:bg-purple-600 text-white',
        orange: 'bg-orange-600 hover:bg-orange-700 dark:bg-orange-700 dark:hover:bg-orange-600 text-white'
    };

    return (
        <button
            onClick={onClick}
            className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-lg ${colorClasses[color]} w-full shadow-sm hover:shadow-md`}
        >
            <Icon className="w-5 h-5" />
            <span>{label}</span>
        </button>
    );
};

const TADashboard = () => {
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
            const response = await taApi.getDashboardStats();
            
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
            setError('An error occurred while fetching dashboard data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const navigateTo = (path) => {
        navigate(path);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading dashboard...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded relative" role="alert">
                <strong className="font-bold">Error!</strong>
                <span className="block sm:inline"> {error}</span>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <h1 className="text-2xl font-bold mb-6 text-zinc-900 dark:text-white">Dashboard</h1>
            
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <DashboardCard 
                    title="Total Courses" 
                    value={stats.totalCourses} 
                    description="Assiged courses"
                    icon={AcademicCapIcon}
                    onClick={() => navigateTo('/ta/courses')}
                />
                <DashboardCard 
                    title="Total Students" 
                    value={stats.totalStudents} 
                    description="Enrolled students"
                    icon={UserGroupIcon}
                    onClick={() => navigateTo('/ta/users')}
                />
                <DashboardCard 
                    title="Total Assignments" 
                    value={stats.totalAssignments} 
                    description="Created assignments"
                    icon={ClipboardDocumentListIcon}
                    onClick={() => navigateTo('/ta/assignments')}
                />
                <DashboardCard 
                    title="Question Bank" 
                    value={stats.totalQuestions} 
                    description="Available questions"
                    icon={QuestionMarkCircleIcon}
                    onClick={() => navigateTo('/ta/question-bank')}
                />
            </div>

            {/* Quick Actions */}
            <div>
                <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
                    {/* <ActionButton 
                        label="Create Course" 
                        icon={PlusCircleIcon} 
                        onClick={() => navigateTo('/ta/courses/new')}
                        color="blue"
                    /> */}
                    <ActionButton 
                        label="Create Assignment" 
                        icon={PlusCircleIcon} 
                        onClick={() => navigateTo('/ta/assignments/new')}
                        color="green"
                    />
                    <ActionButton 
                        label="Add Question" 
                        icon={PlusCircleIcon} 
                        onClick={() => navigateTo('/ta/question-bank/new')}
                        color="purple"
                    />
                </div>
            </div>

            {/* Recent Items */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Courses */}
                <div className="glass-card p-6">
                    <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Recent Courses</h2>
                    <div className="space-y-4">
                        {stats.recentCourses.length > 0 ? (
                            stats.recentCourses.map((course) => (
                                <div 
                                    key={course.id} 
                                    className="p-4 border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800 cursor-pointer rounded-md"
                                    onClick={() => navigateTo(`/ta/courses/${course.id}/content`)}
                                >
                                    <div className="flex justify-between">
                                        <div>
                                            <h3 className="font-medium text-zinc-900 dark:text-white">{course.code}</h3>
                                            <p className="text-sm text-zinc-600 dark:text-zinc-400">{course.name}</p>
                                        </div>
                                        <span className="text-sm text-zinc-500 dark:text-zinc-400">{formatDate(course.createdAt)}</span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-zinc-500 dark:text-zinc-400">No recent courses</p>
                        )}
                    </div>
                </div>

                {/* Recent Assignments */}
                <div className="glass-card p-6">
                    <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Recent Assignments</h2>
                    <div className="space-y-4">
                        {stats.recentAssignments.length > 0 ? (
                            stats.recentAssignments.map((assignment) => (
                                <div 
                                    key={assignment.id} 
                                    className="p-4 border-b border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800 cursor-pointer rounded-md"
                                    onClick={() => navigateTo(`/ta/assignments/${assignment.id}`)}
                                >
                                    <div className="flex justify-between items-center">
                                        <div>
                                            <h3 className="font-medium text-zinc-900 dark:text-white">{assignment.title}</h3>
                                            <p className="text-sm text-zinc-600 dark:text-zinc-400">Due: {formatDate(assignment.due_date)}</p>
                                        </div>
                                        <span className={`px-2 py-1 text-xs rounded-full ${
                                            assignment.status === 'published' 
                                                ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400' 
                                                : 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400'
                                        }`}>
                                            {assignment.status}
                                        </span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-zinc-500 dark:text-zinc-400">No recent assignments</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TADashboard;