import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { 
    AcademicCapIcon,
    BookOpenIcon,
    ClipboardDocumentListIcon,
    ChartBarIcon,
    ArrowRightIcon
} from '@heroicons/react/24/outline';

const placeholderCourses = [
    { id: 1, name: 'Introduction to Programming', code: 'CS101', description: 'Learn the basics of Python programming.', assignments: 3 },
    { id: 2, name: 'Data Structures & Algorithms', code: 'CS102', description: 'Understand fundamental data structures and algorithms.', assignments: 0 },
    { id: 3, name: 'Introduction to ML', code: 'ML101', description: 'A beginner-friendly course on the fundamentals of Machine Learning, including supervised and unsupervised learning techniques.', assignments: 0 }
];

const stats = [
    { 
        title: 'Enrolled Courses', 
        value: placeholderCourses.length,
        icon: BookOpenIcon
    },
    { 
        title: 'Pending Assignments', 
        value: placeholderCourses.reduce((acc, course) => acc + course.assignments, 0),
        icon: ClipboardDocumentListIcon
    },
    { 
        title: 'Overall Progress', 
        value: '0%',
        icon: ChartBarIcon
    }
];

const StudentDashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    return (
        <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900">
            <div className="max-w-7xl mx-auto space-y-8 p-6">
                {/* Logo */}
                <div className="flex justify-center mb-8">
                    <AcademicCapIcon className="h-12 w-12 text-zinc-900 dark:text-white" />
                </div>

                {/* Header Section */}
                <div className="text-center">
                    <h1 className="text-4xl font-bold text-zinc-900 dark:text-white tracking-tight">
                        Welcome back, {user?.first_name || user?.username}
                    </h1>
                    <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                        Here's an overview of your academic progress
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {stats.map((stat, index) => (
                        <div key={index} 
                             className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl p-6 
                                      shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                      dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                            <div className="flex items-center space-x-3">
                                <stat.icon className="h-6 w-6 text-zinc-500 dark:text-zinc-400" />
                                <h3 className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                                    {stat.title}
                                </h3>
                            </div>
                            <p className="mt-4 text-3xl font-bold text-zinc-900 dark:text-white">
                                {stat.value}
                            </p>
                        </div>
                    ))}
                </div>

                {/* Courses Section */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="p-6">
                        <h2 className="text-xl font-bold text-zinc-900 dark:text-white mb-6">
                            My Courses
                        </h2>
                        {placeholderCourses.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {placeholderCourses.map(course => (
                                    <div
                                        key={course.id}
                                        onClick={() => navigate(`/courses/${course.id}`)}
                                        className="group bg-zinc-50/80 dark:bg-zinc-900/30 rounded-xl p-6 
                                                 cursor-pointer transition-all duration-200 
                                                 hover:shadow-[0_4px_12px_-4px_rgba(0,0,0,0.1)] 
                                                 dark:hover:shadow-[0_4px_12px_-4px_rgba(0,0,0,0.3)]"
                                    >
                                        <div className="space-y-3">
                                            <div className="space-y-1">
                                                <h3 className="font-medium text-zinc-900 dark:text-white 
                                                             group-hover:text-zinc-700 dark:group-hover:text-zinc-300">
                                                    {course.name}
                                                </h3>
                                                <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                                    {course.code}
                                                </p>
                                            </div>
                                            <p className="text-sm text-zinc-500 dark:text-zinc-500 line-clamp-2">
                                                {course.description}
                                            </p>
                                            <div className="flex items-center justify-between pt-2 
                                                          text-sm text-zinc-600 dark:text-zinc-400">
                                                <span>Progress: 0%</span>
                                                <span>Assignments: {course.assignments}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12">
                                <p className="text-zinc-600 dark:text-zinc-400 mb-4">
                                    You haven't enrolled in any courses yet.
                                </p>
                                <button
                                    onClick={() => navigate('/courses')}
                                    className="inline-flex items-center text-zinc-900 dark:text-white 
                                             hover:text-zinc-700 dark:hover:text-zinc-300 
                                             font-medium transition-colors"
                                >
                                    Browse Available Courses
                                    <ArrowRightIcon className="ml-2 h-4 w-4" />
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard;