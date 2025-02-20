import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    AcademicCapIcon,
    BookOpenIcon,
    UsersIcon,
    ClipboardDocumentIcon,
    ChartBarIcon
} from '@heroicons/react/24/outline';

const dummyCourses = [
    {
        id: 'cs101',
        name: 'Introduction to Programming',
        code: 'CS101',
        enrolled_students: 150,
        description: 'An introductory course covering basic programming concepts and problem-solving skills.',
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
        description: 'Advanced course focusing on fundamental data structures and algorithm design.',
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
        description: 'Comprehensive study of database design, implementation, and management.',
        assignments: [
            { id: 6, title: 'SQL Fundamentals', submissions: 90, graded: 85 },
            { id: 7, title: 'Database Design', submissions: 88, graded: 0 }
        ]
    }
];

const Courses = () => {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            await new Promise(resolve => setTimeout(resolve, 1000));
            setCourses(dummyCourses);
        } catch (err) {
            setError('Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    const getGradingProgress = (assignments) => {
        const total = assignments.reduce((sum, a) => sum + a.submissions, 0);
        const graded = assignments.reduce((sum, a) => sum + a.graded, 0);
        return Math.round((graded / total) * 100) || 0;
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen bg-zinc-100 dark:bg-zinc-900">
                <div className="text-zinc-600 dark:text-zinc-400">Loading courses...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 dark:text-red-400 text-center p-4">{error}</div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900">
            <div className="max-w-7xl mx-auto space-y-8 p-6">
                {/* Header */}
                <div className="text-center">
                    <div className="flex justify-center mb-8">
                        <AcademicCapIcon className="h-12 w-12 text-zinc-900 dark:text-white" />
                    </div>
                    <h1 className="text-4xl font-bold text-zinc-900 dark:text-white tracking-tight">
                        My Courses
                    </h1>
                    <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                        View and manage your assigned courses
                    </p>
                </div>

                {/* Courses Grid */}
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {courses.map(course => (
                        <div
                            key={course.id}
                            className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                                     shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                     dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]
                                     overflow-hidden"
                        >
                            <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                                            {course.name}
                                        </h2>
                                        <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">
                                            {course.code}
                                        </p>
                                    </div>
                                    <BookOpenIcon className="h-6 w-6 text-zinc-400 dark:text-zinc-500" />
                                </div>
                                <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                    {course.description}
                                </p>
                            </div>

                            <div className="p-6 space-y-4">
                                {/* Course Stats */}
                                <div className="grid grid-cols-3 gap-4">
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-zinc-900 dark:text-white">
                                            {course.enrolled_students}
                                        </div>
                                        <div className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
                                            Students
                                        </div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-zinc-900 dark:text-white">
                                            {course.assignments.length}
                                        </div>
                                        <div className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
                                            Assignments
                                        </div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-zinc-900 dark:text-white">
                                            {getGradingProgress(course.assignments)}%
                                        </div>
                                        <div className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
                                            Graded
                                        </div>
                                    </div>
                                </div>

                                {/* Action Buttons */}
                                <div className="flex space-x-3">
                                    <button
                                        onClick={() => navigate(`/courses/${course.id}`)}
                                        className="flex-1 px-4 py-2 text-sm font-medium 
                                                 bg-zinc-100 dark:bg-zinc-700
                                                 text-zinc-900 dark:text-white rounded-lg
                                                 hover:bg-zinc-200 dark:hover:bg-zinc-600 
                                                 transition-colors duration-200"
                                    >
                                        View Details
                                    </button>
                                    <button
                                        onClick={() => navigate(`/ta/grading?course=${course.id}`)}
                                        className="flex-1 px-4 py-2 text-sm font-medium 
                                                 bg-zinc-800 dark:bg-white
                                                 text-white dark:text-zinc-900 rounded-lg
                                                 hover:bg-zinc-700 dark:hover:bg-zinc-100 
                                                 transition-colors duration-200"
                                    >
                                        Grade Assignments
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Courses;