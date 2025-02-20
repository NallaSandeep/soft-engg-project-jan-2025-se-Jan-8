import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    AcademicCapIcon,
    BookOpenIcon,
    CalendarIcon,
    DocumentCheckIcon,
    UsersIcon,
    ClipboardDocumentCheckIcon
} from '@heroicons/react/24/outline';

// Dummy data
const dummyCourses = [
    {
        id: 'cs101',
        name: 'Introduction to Programming',
        code: 'CS101',
        enrolled_students: 150,
        assignments: [
            {
                id: 1,
                title: 'Variables and Data Types',
                due_date: '2025-03-01',
                submissions_count: 145,
                graded_count: 80,
                total_points: 100
            },
            {
                id: 2,
                title: 'Control Structures',
                due_date: '2025-03-15',
                submissions_count: 142,
                graded_count: 0,
                total_points: 100
            }
        ]
    },
    {
        id: 'cs201',
        name: 'Data Structures and Algorithms',
        code: 'CS201',
        enrolled_students: 125,
        assignments: [
            {
                id: 3,
                title: 'Arrays and Linked Lists',
                due_date: '2025-03-05',
                submissions_count: 120,
                graded_count: 90,
                total_points: 150
            },
            {
                id: 4,
                title: 'Trees and Graphs',
                due_date: '2025-03-20',
                submissions_count: 118,
                graded_count: 0,
                total_points: 150
            }
        ]
    },
    {
        id: 'cs301',
        name: 'Database Systems',
        code: 'CS301',
        enrolled_students: 100,
        assignments: [
            {
                id: 5,
                title: 'SQL Fundamentals',
                due_date: '2025-03-10',
                submissions_count: 98,
                graded_count: 85,
                total_points: 100
            },
            {
                id: 6,
                title: 'Database Design',
                due_date: '2025-03-25',
                submissions_count: 95,
                graded_count: 0,
                total_points: 150
            }
        ]
    }
];

const AssignmentGrading = () => {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchCourses();
    }, []);

    useEffect(() => {
        if (selectedCourse) {
            setAssignments(selectedCourse.assignments || []);
        } else {
            setAssignments([]);
        }
    }, [selectedCourse]);

    const fetchCourses = async () => {
        try {
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            setCourses(dummyCourses);
        } catch (err) {
            console.error('Error loading courses:', err);
            setError('Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    const getGradingProgress = (assignment) => {
        const progress = Math.round((assignment.graded_count / assignment.submissions_count) * 100) || 0;
        return `${progress}% graded`;
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen bg-zinc-100 dark:bg-zinc-900">
                <div className="text-zinc-600 dark:text-zinc-400">Loading assignments...</div>
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
                {/* Logo */}
                <div className="flex justify-center mb-8">
                    <AcademicCapIcon className="h-12 w-12 text-zinc-900 dark:text-white" />
                </div>

                {/* Header */}
                <div className="text-center">
                    <h1 className="text-4xl font-bold text-zinc-900 dark:text-white tracking-tight">
                        Assignment Grading
                    </h1>
                    <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                        Select a course to view pending assignments
                    </p>
                </div>

                {/* Course Selection */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                        <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                            Select Course
                        </h2>
                    </div>
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {courses.map(course => (
                                <button
                                    key={course.id}
                                    className={`group p-6 rounded-xl border text-left transition-all
                                        ${selectedCourse?.id === course.id
                                            ? 'border-zinc-400 dark:border-zinc-500 bg-zinc-50 dark:bg-zinc-700/50'
                                            : 'border-zinc-200 dark:border-zinc-700 hover:border-zinc-300 dark:hover:border-zinc-600'
                                        }`}
                                    onClick={() => setSelectedCourse(course)}
                                >
                                    <div className="flex justify-between items-start mb-4">
                                        <h3 className="font-semibold text-zinc-900 dark:text-white">
                                            {course.name}
                                        </h3>
                                        <BookOpenIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500 
                                                               group-hover:text-zinc-600 dark:group-hover:text-zinc-300" />
                                    </div>
                                    <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-3">
                                        {course.code}
                                    </p>
                                    <div className="flex items-center space-x-2 text-sm text-zinc-500 dark:text-zinc-400">
                                        <UsersIcon className="h-4 w-4" />
                                        <span>{course.enrolled_students} students</span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Assignments List */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                        <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                            {selectedCourse 
                                ? `Assignments for ${selectedCourse.name}`
                                : 'Select a course to view assignments'
                            }
                        </h2>
                    </div>
                    <div className="p-6">
                        {selectedCourse ? (
                            assignments.length > 0 ? (
                                <div className="space-y-4">
                                    {assignments.map(assignment => (
                                        <div
                                            key={assignment.id}
                                            className="group bg-white dark:bg-zinc-800 rounded-xl p-6
                                                     border border-zinc-200 dark:border-zinc-700
                                                     hover:border-zinc-300 dark:hover:border-zinc-600
                                                     transition-all duration-200"
                                        >
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <h3 className="font-semibold text-zinc-900 dark:text-white">
                                                        {assignment.title}
                                                    </h3>
                                                    <div className="flex items-center mt-2 space-x-4">
                                                        <div className="flex items-center text-sm text-zinc-600 dark:text-zinc-400">
                                                            <CalendarIcon className="h-4 w-4 mr-1" />
                                                            Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                        </div>
                                                        <div className="flex items-center text-sm text-zinc-600 dark:text-zinc-400">
                                                            <ClipboardDocumentCheckIcon className="h-4 w-4 mr-1" />
                                                            {getGradingProgress(assignment)}
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex items-center space-x-2">
                                                    <span className="px-3 py-1 text-sm rounded-full 
                                                                   bg-zinc-100 dark:bg-zinc-700
                                                                   text-zinc-600 dark:text-zinc-300">
                                                        {assignment.submissions_count} submissions
                                                    </span>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => navigate(`/assignments/${assignment.id}/grade`)}
                                                className="mt-4 inline-flex items-center text-sm
                                                         text-zinc-600 dark:text-zinc-400
                                                         hover:text-zinc-900 dark:hover:text-white
                                                         transition-colors"
                                            >
                                                <DocumentCheckIcon className="h-4 w-4 mr-2" />
                                                View Submissions
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                                    No assignments available for grading.
                                </div>
                            )
                        ) : (
                            <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                                Select a course to view assignments.
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssignmentGrading;