import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { 
    AcademicCapIcon,
    BookOpenIcon,
    CalendarIcon,
    DocumentCheckIcon,
    UsersIcon,
    ClipboardDocumentCheckIcon
} from '@heroicons/react/24/outline';

const AssignmentGrading = () => {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        fetchCourses();
    }, []);

    useEffect(() => {
        // Check for course query parameter
        const params = new URLSearchParams(location.search);
        const courseId = params.get('course');
        
        if (courseId && courses.length > 0) {
            const course = courses.find(c => c.id === courseId);
            if (course) {
                setSelectedCourse(course);
            }
        }
    }, [courses, location.search]);

    const fetchCourses = async () => {
        try {
            const response = await courseApi.getCourses();
            if (response.success) {
                setCourses(response.data || []);
            } else {
                setError(response.message || 'Failed to load courses');
            }
        } catch (err) {
            console.error('Error loading courses:', err);
            setError(err.message || 'Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    const getGradingProgress = (assignment) => {
        if (!assignment) return 0;
        const submissions = assignment.submissions_count || 0;
        const graded = assignment.graded_count || 0;
        return submissions > 0 ? Math.round((graded / submissions) * 100) : 0;
    };

    const handleCourseSelect = (course) => {
        setSelectedCourse(course);
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'No due date';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
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
            <div className="max-w-7xl mx-auto p-6 space-y-8">
                {/* Header */}
                <div className="text-center">
                    <div className="flex justify-center mb-8">
                        <AcademicCapIcon className="h-12 w-12 text-zinc-900 dark:text-white" />
                    </div>
                    <h1 className="text-4xl font-bold text-zinc-900 dark:text-white tracking-tight">
                        Assignment Grading
                    </h1>
                    <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                        Grade and manage student assignments
                    </p>
                </div>

                {/* Course Selection */}
                {!selectedCourse ? (
                    <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                                  shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                  dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                        <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                            <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                                Select a Course
                            </h2>
                        </div>
                        <div className="p-6">
                            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                {courses.map(course => (
                                    <div
                                        key={course.id}
                                        onClick={() => handleCourseSelect(course)}
                                        className="bg-white dark:bg-zinc-800 rounded-xl p-6
                                                 border border-zinc-200 dark:border-zinc-700
                                                 hover:border-zinc-300 dark:hover:border-zinc-600
                                                 transition-all duration-200 cursor-pointer"
                                    >
                                        <div className="flex justify-between items-start mb-4">
                                            <h3 className="font-semibold text-zinc-900 dark:text-white">
                                                {course.name}
                                            </h3>
                                            <BookOpenIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500" />
                                        </div>
                                        <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
                                            {course.code}
                                        </p>
                                        <div className="flex justify-between text-sm">
                                            <div className="flex items-center space-x-2 text-zinc-500 dark:text-zinc-400">
                                                <UsersIcon className="h-4 w-4" />
                                                <span>{course.enrolled_students || 0}</span>
                                            </div>
                                            <div className="flex items-center space-x-2 text-zinc-500 dark:text-zinc-400">
                                                <ClipboardDocumentCheckIcon className="h-4 w-4" />
                                                <span>{course.assignments?.length || 0} assignments</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : (
                    <>
                        {/* Course Header */}
                        <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl p-6
                                      shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                      dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h2 className="text-2xl font-semibold text-zinc-900 dark:text-white">
                                        {selectedCourse.name}
                                    </h2>
                                    <p className="text-zinc-600 dark:text-zinc-400 mt-1">
                                        {selectedCourse.code}
                                    </p>
                                </div>
                                <button 
                                    onClick={() => setSelectedCourse(null)}
                                    className="px-4 py-2 text-sm font-medium 
                                             bg-zinc-100 dark:bg-zinc-700
                                             text-zinc-900 dark:text-white rounded-lg
                                             hover:bg-zinc-200 dark:hover:bg-zinc-600 
                                             transition-colors duration-200"
                                >
                                    Change Course
                                </button>
                            </div>
                        </div>

                        {/* Assignments List */}
                        <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                                      shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                                      dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                            <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                                <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                                    Assignments
                                </h2>
                            </div>
                            <div className="p-6">
                                {selectedCourse.assignments && selectedCourse.assignments.length > 0 ? (
                                    <div className="space-y-4">
                                        {selectedCourse.assignments.map(assignment => (
                                            <div 
                                                key={assignment.id}
                                                className="bg-white dark:bg-zinc-800 rounded-xl p-6
                                                         border border-zinc-200 dark:border-zinc-700
                                                         hover:border-zinc-300 dark:hover:border-zinc-600
                                                         transition-all duration-200"
                                            >
                                                <div className="flex flex-col md:flex-row md:justify-between md:items-center">
                                                    <div className="mb-4 md:mb-0">
                                                        <h3 className="text-lg font-semibold text-zinc-900 dark:text-white">
                                                            {assignment.title}
                                                        </h3>
                                                        <div className="flex items-center mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                                                            <CalendarIcon className="h-4 w-4 mr-2" />
                                                            <span>Due: {formatDate(assignment.due_date)}</span>
                                                        </div>
                                                    </div>
                                                    
                                                    <div className="flex flex-col md:flex-row items-start md:items-center space-y-3 md:space-y-0 md:space-x-4">
                                                        <div className="flex items-center space-x-2">
                                                            <div className="w-32 bg-zinc-200 dark:bg-zinc-700 rounded-full h-2.5">
                                                                <div 
                                                                    className="bg-zinc-800 dark:bg-white h-2.5 rounded-full" 
                                                                    style={{ width: `${getGradingProgress(assignment)}%` }}
                                                                ></div>
                                                            </div>
                                                            <span className="text-sm text-zinc-600 dark:text-zinc-400">
                                                                {getGradingProgress(assignment)}%
                                                            </span>
                                                        </div>
                                                        
                                                        <button
                                                            onClick={() => navigate(`/courses/${selectedCourse.id}/assignments/${assignment.id}`)}
                                                            className="px-4 py-2 text-sm font-medium 
                                                                     bg-zinc-800 dark:bg-white
                                                                     text-white dark:text-zinc-900 rounded-lg
                                                                     hover:bg-zinc-700 dark:hover:bg-zinc-100 
                                                                     transition-colors duration-200"
                                                        >
                                                            Grade Submissions
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                                        No assignments available for this course.
                                    </div>
                                )}
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default AssignmentGrading; 