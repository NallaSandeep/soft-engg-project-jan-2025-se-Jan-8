import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../services/apiService';
import { useAuth } from '../hooks/useAuth';

const Dashboard = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isDark, setIsDark] = useState(false);
    const navigate = useNavigate();
    const { user } = useAuth();

    useEffect(() => {
        fetchData();
        // Check system preference for dark mode
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setIsDark(true);
        }
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            setError('');
            const response = await courseApi.getCourses();
            if (response.success && response.data) {
                setCourses(response.data);
            } else {
                setError('No courses available');
            }
        } catch (err) {
            console.error('Dashboard error:', err);
            setError('Failed to fetch courses');
        } finally {
            setLoading(false);
        }
    };

    const toggleTheme = () => {
        setIsDark(!isDark);
        document.documentElement.classList.toggle('dark');
    };

    if (loading) {
        return (
            <div className={`flex justify-center items-center min-h-screen ${isDark ? 'bg-dark-primary' : 'bg-light-primary'}`}>
                <div className="animate-pulse-subtle">
                    <svg className="w-12 h-12 text-brand-primary animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                </div>
            </div>
        );
    }

    return (
        <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-dark-primary' : 'bg-light-primary'}`}>
            <div className="p-6 max-w-7xl mx-auto">
                {/* Header Section */}
                <div className={`flex justify-between items-center mb-8 p-6 rounded-xl shadow-soft ${
                    isDark ? 'bg-dark-secondary' : 'bg-light-secondary'
                }`}>
                    <div className="space-y-1">
                        <h1 className={`text-3xl font-bold ${
                            isDark ? 'text-dark-text-primary' : 'text-light-text-primary'
                        }`}>
                            Welcome back, {user?.first_name || user?.username}! 👋
                        </h1>
                        <p className={isDark ? 'text-dark-text-secondary' : 'text-light-text-secondary'}>
                            Track your learning journey
                        </p>
                    </div>
                    <button
                        onClick={toggleTheme}
                        className={`p-3 rounded-lg transition-all duration-200 ${
                            isDark 
                                ? 'bg-dark-accent hover:bg-dark-hover text-dark-text-primary' 
                                : 'bg-light-accent hover:bg-light-hover text-light-text-primary'
                        }`}
                    >
                        {isDark ? '🌞' : '🌙'}
                    </button>
                </div>

                {/* Main Content */}
                {error ? (
                    <div className={`rounded-xl shadow-card p-8 text-center ${
                        isDark ? 'bg-dark-secondary' : 'bg-light-secondary'
                    }`}>
                        <p className={`mb-6 ${isDark ? 'text-dark-text-secondary' : 'text-light-text-secondary'}`}>
                            {error}
                        </p>
                        <button
                            onClick={() => navigate('/courses')}
                            className="bg-brand-primary hover:bg-brand-primary-hover text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
                        >
                            Browse Available Courses
                        </button>
                    </div>
                ) : courses.length === 0 ? (
                    <div className={`rounded-xl shadow-card p-8 text-center animate-fade-in ${
                        isDark ? 'bg-dark-secondary' : 'bg-light-secondary'
                    }`}>
                        <svg className="w-16 h-16 mx-auto mb-4 text-brand-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                        </svg>
                        <p className={`mb-6 ${isDark ? 'text-dark-text-secondary' : 'text-light-text-secondary'}`}>
                            Ready to start learning? Enroll in your first course!
                        </p>
                        <button
                            onClick={() => navigate('/courses')}
                            className="bg-brand-primary hover:bg-brand-primary-hover text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
                        >
                            Browse Available Courses
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {courses.map(course => (
                            <div
                                key={course.id}
                                onClick={() => navigate(`/courses/${course.id}`)}
                                className={`group rounded-xl shadow-card hover:shadow-dropdown transition-all duration-200 cursor-pointer transform hover:-translate-y-1 ${
                                    isDark ? 'bg-dark-secondary hover:bg-dark-hover' : 'bg-light-secondary hover:bg-light-hover'
                                }`}
                            >
                                <div className="p-6 space-y-4">
                                    <h2 className={`text-xl font-semibold group-hover:text-brand-primary transition-colors ${
                                        isDark ? 'text-dark-text-primary' : 'text-light-text-primary'
                                    }`}>
                                        {course.name}
                                    </h2>
                                    <p className={`text-sm ${isDark ? 'text-dark-text-secondary' : 'text-light-text-secondary'}`}>
                                        {course.code}
                                    </p>
                                    <div className="space-y-3">
                                        <div className="flex justify-between text-sm">
                                            <span className={isDark ? 'text-dark-text-tertiary' : 'text-light-text-tertiary'}>
                                                Progress
                                            </span>
                                            <span className="text-brand-primary">0%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                            <div className="bg-brand-primary h-2 rounded-full transition-all duration-300" 
                                                 style={{width: '0%'}}
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;