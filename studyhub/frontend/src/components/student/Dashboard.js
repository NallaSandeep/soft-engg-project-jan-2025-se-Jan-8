import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi, personalApi, assignmentApi } from '../../services/apiService';
import { Card } from '../common/Card';
import { 
    ExclamationCircleIcon, 
    ClockIcon, 
    ArrowTrendingUpIcon,
    BookOpenIcon
} from '@heroicons/react/24/outline';

const Dashboard = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [personalResources, setPersonalResources] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [overallProgress, setOverallProgress] = useState({
        totalCourses: 0,
        completedCourses: 0,
        totalItems: 0,
        completedItems: 0,
        pendingAssignments: {
            urgent: [], // Due within 48 hours or overdue
            upcoming: [], // Due within 7 days
            practice: [], // Practice assignments not attempted or can be improved
            total: 0,
            totalGradedAssignments: 0,
            completedGradedAssignments: 0,
            gradedAssignmentPercentage: 0
        },
        percentage: 0
    });

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const calculatePendingAssignments = (courses) => {
        const now = new Date();
        const urgent = [];
        const upcoming = [];
        const practice = [];
        let totalGradedAssignments = 0;
        let completedGradedAssignments = 0;

        courses.forEach(course => {
            course.weeks?.forEach(week => {
                week.assignments?.forEach(assignment => {
                    if (!assignment.is_published) return;
                    
                    const dueDate = new Date(assignment.due_date);
                    const timeDiff = dueDate - now;
                    const daysUntilDue = timeDiff / (1000 * 60 * 60 * 24);
                    const lastSubmission = assignment.last_submission;

                    if (assignment.type === 'graded') {
                        totalGradedAssignments++;
                        if (lastSubmission && lastSubmission.status === 'submitted') {
                            completedGradedAssignments++;
                        }

                        // For graded assignments
                        if (!lastSubmission) {
                            // No submission yet
                            if (timeDiff < 0) {
                                // Overdue
                                urgent.push({ ...assignment, course });
                            } else if (daysUntilDue <= 2) {
                                // Due within 48 hours
                                urgent.push({ ...assignment, course });
                            } else if (daysUntilDue <= 7) {
                                // Due within a week
                                upcoming.push({ ...assignment, course });
                            }
                        }
                    } else {
                        // For practice assignments
                        if (!lastSubmission || (lastSubmission.score < assignment.points_possible)) {
                            practice.push({ ...assignment, course });
                        }
                    }
                });
            });
        });

        return {
            urgent,
            upcoming,
            practice,
            total: urgent.length + upcoming.length + practice.length,
            totalGradedAssignments,
            completedGradedAssignments,
            gradedAssignmentPercentage: totalGradedAssignments > 0 ? Math.round((completedGradedAssignments / totalGradedAssignments) * 100) : 0
        };
    };

    const fetchDashboardData = async () => {
        try {
            setError(null);
            const [coursesResponse, resourcesResponse, completedAssignmentsResponse, allAssignmentsResponse] = await Promise.all([
                courseApi.getCourses(),
                personalApi.getResources(),
                assignmentApi.getAssignments({ status: 'completed' }),
                assignmentApi.getAssignments()
            ]);
            
            if (coursesResponse.success) {
                const courses = coursesResponse.data;
                setCourses(courses);

                // Fetch progress for each course
                const progressPromises = courses.map(course => 
                    courseApi.getCourseProgress(course.id)
                );
                
                const progressResponses = await Promise.all(progressPromises);
                
                // Calculate overall progress
                let totalItems = 0;
                let completedItems = 0;
                let completedCourses = 0;

                progressResponses.forEach((response, index) => {
                    if (response.success) {
                        const progress = response.data;
                        totalItems += progress.total_items;
                        completedItems += progress.completed_items;
                        
                        // Consider a course completed if progress is 100%
                        if (progress.percentage === 100) {
                            completedCourses++;
                        }

                        // Add progress to course object
                        courses[index].progress = progress;
                    }
                });

                // Get all published graded assignments
                const allAssignments = allAssignmentsResponse.success ? allAssignmentsResponse.data : [];
                const gradedAssignments = allAssignments.filter(a => a.type === 'graded' && a.is_published);
                
                // Get completed assignments
                const completedAssignments = completedAssignmentsResponse.success ? completedAssignmentsResponse.data : [];
                const completedGradedAssignments = completedAssignments.filter(a => 
                    a.type === 'graded' && a.submission && a.submission.status === 'submitted'
                );

                // Calculate pending assignments
                const now = new Date();
                const urgent = [];
                const upcoming = [];
                const practice = [];

                allAssignments.forEach(assignment => {
                    if (!assignment.is_published) return;

                    const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;
                    const timeDiff = dueDate ? dueDate - now : Infinity;
                    const daysUntilDue = timeDiff / (1000 * 60 * 60 * 24);

                    // Skip if assignment is already completed
                    const isCompleted = completedAssignments.some(ca => ca.id === assignment.id);
                    if (isCompleted) return;

                    if (assignment.type === 'graded') {
                        if (!dueDate || timeDiff < 0) {
                            // Overdue or no due date
                            urgent.push(assignment);
                        } else if (daysUntilDue <= 2) {
                            // Due within 48 hours
                            urgent.push(assignment);
                        } else if (daysUntilDue <= 7) {
                            // Due within a week
                            upcoming.push(assignment);
                        }
                    } else if (assignment.type === 'practice') {
                        practice.push(assignment);
                    }
                });

                setCourses(courses);
                setOverallProgress({
                    totalCourses: courses.length,
                    completedCourses,
                    totalItems,
                    completedItems,
                    pendingAssignments: {
                        urgent,
                        upcoming,
                        practice,
                        total: urgent.length + upcoming.length + practice.length,
                        totalGradedAssignments: gradedAssignments.length,
                        completedGradedAssignments: completedGradedAssignments.length,
                        gradedAssignmentPercentage: gradedAssignments.length > 0 ? 
                            Math.round((completedGradedAssignments.length / gradedAssignments.length) * 100) : 0
                    },
                    percentage: totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0
                });
            }

            if (resourcesResponse.success) {
                setPersonalResources(resourcesResponse.data);
            }
        } catch (err) {
            console.error('Error loading dashboard:', err);
            setError(err.message || 'Failed to load dashboard');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
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
        <div className="container mx-auto p-6">
            {/* Overall Progress Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Course Completion Card */}
                <Card>
                    <div className="p-4">
                        <h3 className="text-lg font-medium text-zinc-900 dark:text-white mb-2">Course Completion</h3>
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="text-3xl font-bold text-blue-500 dark:text-blue-400">
                                    {overallProgress.completedCourses}/{overallProgress.totalCourses}
                                </p>
                                <p className="text-sm text-zinc-600 dark:text-zinc-400">Courses Completed</p>
                            </div>
                            <div className="w-16 h-16">
                                <svg viewBox="0 0 36 36" className="circular-chart">
                                    <path
                                        d="M18 2.0845
                                            a 15.9155 15.9155 0 0 1 0 31.831
                                            a 15.9155 15.9155 0 0 1 0 -31.831"
                                        fill="none"
                                        stroke="#eee"
                                        strokeWidth="3"
                                    />
                                    <path
                                        d="M18 2.0845
                                            a 15.9155 15.9155 0 0 1 0 31.831
                                            a 15.9155 15.9155 0 0 1 0 -31.831"
                                        fill="none"
                                        stroke="#3b82f6"
                                        strokeWidth="3"
                                        strokeDasharray={`${(overallProgress.completedCourses / overallProgress.totalCourses) * 100}, 100`}
                                    />
                                </svg>
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Content Progress Card */}
                <Card>
                    <div className="p-4">
                        <h3 className="text-lg font-medium text-zinc-900 dark:text-white mb-2">Content Progress</h3>
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="text-3xl font-bold text-green-500 dark:text-green-400">
                                    {overallProgress.completedItems}/{overallProgress.totalItems}
                                </p>
                                <p className="text-sm text-zinc-600 dark:text-zinc-400">Items Completed</p>
                            </div>
                            <div className="w-16 h-16">
                                <svg viewBox="0 0 36 36" className="circular-chart">
                                    <path
                                        d="M18 2.0845
                                            a 15.9155 15.9155 0 0 1 0 31.831
                                            a 15.9155 15.9155 0 0 1 0 -31.831"
                                        fill="none"
                                        stroke="#eee"
                                        strokeWidth="3"
                                    />
                                    <path
                                        d="M18 2.0845
                                            a 15.9155 15.9155 0 0 1 0 31.831
                                            a 15.9155 15.9155 0 0 1 0 -31.831"
                                        fill="none"
                                        stroke="#22c55e"
                                        strokeWidth="3"
                                        strokeDasharray={`${overallProgress.percentage}, 100`}
                                    />
                                </svg>
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Assignments Progress Card */}
                <Card>
                    <div className="p-4">
                        <h3 className="text-lg font-medium text-zinc-900 dark:text-white mb-2">Graded Assignments</h3>
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="text-3xl font-bold text-yellow-500 dark:text-yellow-400">
                                    {overallProgress.pendingAssignments.completedGradedAssignments}/{overallProgress.pendingAssignments.totalGradedAssignments}
                                </p>
                                <p className="text-sm text-zinc-600 dark:text-zinc-400">Completed</p>
                            </div>
                            <div className="w-16 h-16">
                                <svg viewBox="0 0 36 36" className="circular-chart">
                                    <path
                                        d="M18 2.0845
                                            a 15.9155 15.9155 0 0 1 0 31.831
                                            a 15.9155 15.9155 0 0 1 0 -31.831"
                                        fill="none"
                                        stroke="#eee"
                                        strokeWidth="3"
                                    />
                                    <path
                                        d="M18 2.0845
                                            a 15.9155 15.9155 0 0 1 0 31.831
                                            a 15.9155 15.9155 0 0 1 0 -31.831"
                                        fill="none"
                                        stroke="#eab308"
                                        strokeWidth="3"
                                        strokeDasharray={`${overallProgress.pendingAssignments.gradedAssignmentPercentage}, 100`}
                                    />
                                </svg>
                            </div>
                        </div>
                        {overallProgress.pendingAssignments.totalGradedAssignments > 0 && (
                            <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-2">
                                {overallProgress.pendingAssignments.gradedAssignmentPercentage}% completed
                            </p>
                        )}
                    </div>
                </Card>
            </div>

            {/* Course List */}
            <div className="mb-8">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">My Courses</h2>
                    <button
                        onClick={() => navigate('/student/courses')}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm"
                    >
                        View All →
                    </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {courses.map(course => (
                        <Card key={course.id}>
                            <div 
                                className="p-4 cursor-pointer"
                                onClick={() => navigate(`/student/courses/${course.id}`)}
                            >
                                <h3 className="text-lg font-medium text-zinc-900 dark:text-white mb-2">
                                    {course.name}
                                </h3>
                                <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
                                    {course.code}
                                </p>
                                {course.progress && (
                                    <div>
                                        <div className="flex justify-between text-sm text-zinc-600 dark:text-zinc-400 mb-1">
                                            <span>Progress</span>
                                            <span>{course.progress.percentage}%</span>
                                        </div>
                                        <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-2">
                                            <div 
                                                className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                                                style={{ width: `${course.progress.percentage}%` }}
                                            ></div>
                                        </div>
                                        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                            {course.progress.completed_items} of {course.progress.total_items} items completed
                                        </p>
                                    </div>
                                )}
                            </div>
                        </Card>
                    ))}
                </div>
            </div>

            {/* Personal Resources */}
            <div>
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">Personal Resources</h2>
                    <button
                        onClick={() => navigate('/student/personal-resources')}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm"
                    >
                        View All →
                    </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {personalResources.slice(0, 3).map(resource => (
                        <Card key={resource.id}>
                            <div 
                                className="p-4 cursor-pointer"
                                onClick={() => navigate(`/student/personal-resources/${resource.id}`)}
                            >
                                <h3 className="text-lg font-medium text-zinc-900 dark:text-white mb-2">
                                    {resource.name}
                                </h3>
                                <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                                    {resource.description}
                                </p>
                                <p className="text-xs text-zinc-500 dark:text-zinc-400">
                                    {resource.files?.length || 0} files
                                </p>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard; 