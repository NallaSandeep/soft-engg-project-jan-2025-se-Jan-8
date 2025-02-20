import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    AcademicCapIcon,
    BookOpenIcon,
    ClipboardDocumentListIcon,
    ChartBarIcon,
    UsersIcon,
    ClipboardDocumentIcon
} from '@heroicons/react/24/outline';

// Dummy course data
const dummyCourses = [
    {
        id: 'cs101',
        name: 'Introduction to Programming',
        code: 'CS101',
        enrolled_students: 150,
        assignments: [
            { id: 1, title: 'Variables and Data Types', submissions: 120, graded: 90 },
            { id: 2, title: 'Control Structures', submissions: 115, graded: 80 }
        ]
    },
    {
        id: 'cs201',
        name: 'Data Structures and Algorithms',
        code: 'CS201',
        enrolled_students: 125,
        assignments: [
            { id: 3, title: 'Arrays and Linked Lists', submissions: 100, graded: 95 },
            { id: 4, title: 'Trees and Graphs', submissions: 98, graded: 90 },
            { id: 5, title: 'Dynamic Programming', submissions: 95, graded: 0 }
        ]
    },
    {
        id: 'cs301',
        name: 'Database Systems',
        code: 'CS301',
        enrolled_students: 100,
        assignments: [
            { id: 6, title: 'SQL Fundamentals', submissions: 90, graded: 85 },
            { id: 7, title: 'Database Design', submissions: 88, graded: 0 }
        ]
    }
];

const TADashboard = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            setCourses(dummyCourses);
        } catch (err) {
            console.error('Error loading courses:', err);
            setError('Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    // Calculate total pending assignments
    const pendingAssignments = courses.reduce((total, course) => {
        return total + course.assignments.filter(a => a.submissions > a.graded).length;
    }, 0);

    // Calculate assignments graded this week (dummy calculation)
    const gradedThisWeek = courses.reduce((total, course) => {
        return total + course.assignments.reduce((sum, assignment) => sum + assignment.graded, 0);
    }, 0);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen bg-zinc-100 dark:bg-zinc-900">
                <div className="text-zinc-600 dark:text-zinc-400">Loading dashboard...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 dark:text-red-400 text-center p-4">{error}</div>
        );
    }

    const stats = [
        { 
            title: 'Assigned Courses', 
            value: courses.length,
            icon: BookOpenIcon
        },
        { 
            title: 'Pending Assignments', 
            value: pendingAssignments,
            icon: ClipboardDocumentListIcon
        },
        { 
            title: 'Graded This Week', 
            value: gradedThisWeek,
            icon: ChartBarIcon
        }
    ];

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
                        Teaching Assistant Dashboard
                    </h1>
                    <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                        Manage your assigned courses and assignments
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {stats.map((stat, index) => (
                        <div key={index} 
                            className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl p-6 
                                     shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                     dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]"
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

                {/* Courses Section */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                        <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                            My Courses
                        </h2>
                    </div>
                    
                    <div className="p-6">
                        {courses.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {courses.map(course => (
                                    <div 
                                        key={course.id}
                                        onClick={() => navigate(`/courses/${course.id}`)}
                                        className="group bg-white dark:bg-zinc-800 rounded-xl p-6
                                                 border border-zinc-200 dark:border-zinc-700
                                                 hover:border-zinc-300 dark:hover:border-zinc-600
                                                 transition-all duration-200 cursor-pointer"
                                    >
                                        <div className="flex justify-between items-start mb-4">
                                            <h3 className="font-semibold text-zinc-900 dark:text-white">
                                                {course.name}
                                            </h3>
                                            <BookOpenIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500 
                                                                   group-hover:text-zinc-600 dark:group-hover:text-zinc-300
                                                                   transition-colors" />
                                        </div>
                                        <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
                                            {course.code}
                                        </p>
                                        <div className="flex justify-between text-sm">
                                            <div className="flex items-center space-x-2 text-zinc-500 dark:text-zinc-400">
                                                <UsersIcon className="h-4 w-4" />
                                                <span>{course.enrolled_students}</span>
                                            </div>
                                            <div className="flex items-center space-x-2 text-zinc-500 dark:text-zinc-400">
                                                <ClipboardDocumentIcon className="h-4 w-4" />
                                                <span>{course.assignments.length}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                                No courses assigned yet.
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TADashboard;