import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi, personalApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';
import { DocumentTextIcon, BookOpenIcon, ClockIcon, ChartBarIcon } from '@heroicons/react/24/outline';

const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="bg-zinc-50 dark:bg-zinc-800 rounded-lg p-6 border border-zinc-200 dark:border-zinc-700">
        <div className="flex items-center justify-between">
            <div>
                <p className="text-zinc-600 dark:text-gray-400 text-sm">{title}</p>
                <p className={`text-3xl font-bold ${color}`}>{value}</p>
            </div>
            <div className={`p-3 rounded-full ${color.replace('text-', 'bg-').replace('00', '00/20')}`}>
                <Icon className={`h-6 w-6 ${color}`} />
            </div>
        </div>
    </div>
);

const Dashboard = () => {
    const [courses, setCourses] = useState([]);
    const [resources, setResources] = useState([]);
    const [stats, setStats] = useState({
        enrolledCourses: 0,
        pendingAssignments: 0,
        overallProgress: 0,
        totalResources: 0
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const { user } = useAuth();

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const [coursesResponse, resourcesResponse] = await Promise.all([
                courseApi.getCourses(),
                personalApi.getPersonalResources()
            ]);

            // Extract data from responses
            const courses = Array.isArray(coursesResponse.data) ? coursesResponse.data : [];
            const resources = Array.isArray(resourcesResponse.data) ? resourcesResponse.data : [];

            setCourses(courses);
            setResources(resources);
            setStats({
                enrolledCourses: courses.length,
                pendingAssignments: courses.reduce((acc, course) => 
                    acc + (course.pending_assignments || 0), 0),
                overallProgress: courses.length ? 
                    Math.round(courses.reduce((acc, course) => 
                        acc + (course.progress || 0), 0) / courses.length) : 0,
                totalResources: resources.length
            });
        } catch (err) {
            console.error('Error loading dashboard data:', err);
            setError('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <p className="text-zinc-600 dark:text-zinc-400">Loading dashboard...</p>
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
            <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">Welcome, {user?.first_name || 'Student'}!</h1>
            <p className="text-zinc-600 dark:text-zinc-400 mb-6">Here's an overview of your courses and progress</p>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <StatCard 
                    title="Enrolled Courses" 
                    value={stats.enrolledCourses}
                    icon={BookOpenIcon}
                    color="text-blue-500"
                />
                <StatCard 
                    title="Pending Assignments" 
                    value={stats.pendingAssignments}
                    icon={ClockIcon}
                    color="text-yellow-500"
                />
                <StatCard 
                    title="Overall Progress" 
                    value={`${stats.overallProgress}%`}
                    icon={ChartBarIcon}
                    color="text-green-500"
                />
                <StatCard 
                    title="Personal Resources" 
                    value={stats.totalResources}
                    icon={DocumentTextIcon}
                    color="text-purple-500"
                />
            </div>

            {/* My Courses Section */}
            <div className="bg-zinc-50 dark:bg-zinc-800 rounded-lg p-6 mb-6 border border-zinc-200 dark:border-zinc-700">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">My Courses</h2>
                    <button
                        onClick={() => navigate('/student/courses')}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm"
                    >
                        View All →
                    </button>
                </div>
                {courses.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {courses.slice(0, 3).map(course => (
                            <div
                                key={course.id}
                                className="bg-white dark:bg-zinc-700 rounded-lg p-4 hover:bg-zinc-100 dark:hover:bg-zinc-600 cursor-pointer transition-colors border border-zinc-200 dark:border-zinc-600"
                                onClick={() => navigate(`/student/courses/${course.id}`)}
                            >
                                <h3 className="font-medium text-zinc-900 dark:text-white mb-2">{course.name}</h3>
                                <p className="text-sm text-zinc-600 dark:text-gray-400 mb-4">{course.code}</p>
                                <div className="flex justify-between text-sm text-zinc-600 dark:text-gray-400">
                                    <span>Progress: {course.progress || 0}%</span>
                                    <span>{course.pending_assignments || 0} pending</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <p className="text-zinc-600 dark:text-gray-400 mb-4">You haven't enrolled in any courses yet.</p>
                        <button
                            onClick={() => navigate('/student/courses')}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                        >
                            Browse Courses
                        </button>
                    </div>
                )}
            </div>

            {/* Personal Resources Section */}
            <div className="bg-zinc-50 dark:bg-zinc-800 rounded-lg p-6 border border-zinc-200 dark:border-zinc-700">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">Personal Resources</h2>
                    <button
                        onClick={() => navigate('/personal-resources')}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm"
                    >
                        View All →
                    </button>
                </div>
                {resources.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {resources.slice(0, 3).map(resource => (
                            <div
                                key={resource.id}
                                className="bg-white dark:bg-zinc-700 rounded-lg p-4 hover:bg-zinc-100 dark:hover:bg-zinc-600 cursor-pointer transition-colors border border-zinc-200 dark:border-zinc-600"
                                onClick={() => navigate(`/personal-resources/${resource.id}`)}
                            >
                                <h3 className="font-medium text-zinc-900 dark:text-white mb-2">{resource.name}</h3>
                                <p className="text-sm text-zinc-600 dark:text-gray-400 mb-4">{resource.description}</p>
                                <div className="flex justify-between text-sm text-zinc-600 dark:text-gray-400">
                                    <span>{resource.files?.length || 0} files</span>
                                    <span>Updated {new Date(resource.updated_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <p className="text-zinc-600 dark:text-gray-400 mb-4">You haven't created any resources yet.</p>
                        <button
                            onClick={() => navigate('/personal-resources')}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                        >
                            Create Resource
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard; 