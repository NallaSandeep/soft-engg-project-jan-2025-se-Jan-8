import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    AcademicCapIcon,
    BookOpenIcon,
    UsersIcon,
    ClipboardDocumentListIcon,
    QuestionMarkCircleIcon,
    CalendarIcon,
    CheckCircleIcon,
    ClockIcon
} from '@heroicons/react/24/outline';

const AdminDashboard = () => {
    const navigate = useNavigate();
    
    const stats = {
        totalCourses: 4,
        totalStudents: 150,
        totalAssignments: 10,
        totalQuestions: 50,
        recentCourses: [
            { id: 1, name: 'Introduction to Programming', code: 'CS101', created_at: '2025-02-01' },
            { id: 2, name: 'Data Structures', code: 'CS102', created_at: '2025-01-20' },
            { id: 3, name: 'Introduction to ML', code: 'ML101', created_at: '2025-01-20' }
        ],
        recentAssignments: [
            { id: 1, title: 'Practice Assignment 1.1', due_date: '2025-02-10', is_published: true },
            { id: 2, title: 'Graded Assignment 1', due_date: '2025-02-15', is_published: false },
            { id: 3, title: 'Practice Assignment 2.1', due_date: '2025-02-10', is_published: true }
        ]
    };

    const quickActions = [
        { text: 'Create Course', route: '/admin/courses/new', icon: BookOpenIcon },
        { text: 'Add Student', route: '/admin/users/new', icon: UsersIcon },
        { text: 'Create Assignment', route: '/admin/assignments/new', icon: ClipboardDocumentListIcon },
        { text: 'Add Question', route: '/admin/question-bank/new', icon: QuestionMarkCircleIcon }
    ];
    
    return (
        <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900">
            <div className="max-w-7xl mx-auto space-y-8 p-6">
                {/* Logo */}
                {/* <div className="flex justify-center mb-8">
                    <AcademicCapIcon className="h-12 w-12 text-zinc-900 dark:text-white" />
                </div> */}

                {/* Header */}
                {/* <div className="text-center">
                    <h1 className="text-4xl font-bold text-zinc-900 dark:text-white tracking-tight">
                        Admin Dashboard
                    </h1>
                    <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                        Manage your platform's courses, users, and content
                    </p>
                </div> */}

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[
                        { title: 'Total Courses', value: stats.totalCourses, icon: BookOpenIcon },
                        { title: 'Total Students', value: stats.totalStudents, icon: UsersIcon },
                        { title: 'Total Assignments', value: stats.totalAssignments, icon: ClipboardDocumentListIcon },
                        { title: 'Question Bank', value: stats.totalQuestions, icon: QuestionMarkCircleIcon }
                    ].map((stat, index) => (
                        <div key={index} 
                             className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl p-6
                                      shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                      dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]
                                      cursor-pointer hover:scale-105 transition-all duration-200"
                             onClick={() => navigate(stat.route)}
                        >
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

                {/* Quick Actions */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                        <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                            Quick Actions
                        </h2>
                    </div>
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {quickActions.map((action, index) => (
                                <button
                                    key={index}
                                    onClick={() => navigate(action.route)}
                                    className="flex items-center space-x-2 px-4 py-2 rounded-lg
                                             bg-zinc-800 dark:bg-white
                                             text-white dark:text-zinc-900
                                             hover:bg-zinc-700 dark:hover:bg-zinc-100
                                             transition-colors duration-200"
                                >
                                    <action.icon className="h-5 w-5" />
                                    <span>{action.text}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Recent Courses */}
                    <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                                  shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                  dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                        <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                                Recent Courses
                            </h2>
                        </div>
                        <div className="p-6">
                            <div className="space-y-4">
                                {stats.recentCourses.map(course => (
                                    <div
                                        key={course.id}
                                        onClick={() => navigate(`/admin/courses/${course.id}`)}
                                        className="group flex justify-between items-center p-4
                                                 bg-white dark:bg-zinc-800 rounded-lg
                                                 border border-zinc-200 dark:border-zinc-700
                                                 hover:border-zinc-300 dark:hover:border-zinc-600
                                                 cursor-pointer transition-all duration-200"
                                    >
                                        <div className="flex items-center space-x-3">
                                            <BookOpenIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500" />
                                            <div>
                                                <h3 className="font-medium text-zinc-900 dark:text-white">
                                                    {course.name}
                                                </h3>
                                                <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                                    {course.code}
                                                </p>
                                            </div>
                                        </div>
                                        <CalendarIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Recent Assignments */}
                    <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                                  shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                  dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                        <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                                Recent Assignments
                            </h2>
                        </div>
                        <div className="p-6">
                            <div className="space-y-4">
                                {stats.recentAssignments.map(assignment => (
                                    <div
                                        key={assignment.id}
                                        onClick={() => navigate(`/admin/assignments/${assignment.id}`)}
                                        className="group flex justify-between items-center p-4
                                                 bg-white dark:bg-zinc-800 rounded-lg
                                                 border border-zinc-200 dark:border-zinc-700
                                                 hover:border-zinc-300 dark:hover:border-zinc-600
                                                 cursor-pointer transition-all duration-200"
                                    >
                                        <div className="flex items-center space-x-3">
                                            <ClipboardDocumentListIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500" />
                                            <div>
                                                <h3 className="font-medium text-zinc-900 dark:text-white">
                                                    {assignment.title}
                                                </h3>
                                                <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                                    Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                        {assignment.is_published ? (
                                            <CheckCircleIcon className="h-5 w-5 text-emerald-500" />
                                        ) : (
                                            <ClockIcon className="h-5 w-5 text-amber-500" />
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;