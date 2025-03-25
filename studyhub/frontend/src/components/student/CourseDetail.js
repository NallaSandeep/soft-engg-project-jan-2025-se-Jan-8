import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { Card } from '../common/Card';
import { ChartBarIcon, BookOpenIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/outline';

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

const CourseDetail = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            setLoading(true);
            const [courseResponse, progressResponse] = await Promise.all([
                courseApi.getCourseContent(courseId),
                courseApi.getCourseProgress(courseId)
            ]);

            if (courseResponse.success) {
                setCourse(courseResponse.data.data.course);
            } else {
                setError('Failed to load course content');
            }

            if (progressResponse.success) {
                setProgress(progressResponse.data);
            }
        } catch (err) {
            setError('Failed to load course content');
            console.error('Error loading course content:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading course content...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 dark:text-red-400 text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                {error}
            </div>
        );
    }

    if (!course) {
        return (
            <div className="text-center py-8">
                <p className="text-zinc-600 dark:text-zinc-400">Course not found</p>
                <button
                    onClick={() => navigate('/student/courses')}
                    className="mt-4 text-blue-500 dark:text-blue-400 hover:text-blue-600 dark:hover:text-blue-300"
                >
                    Return to Courses
                </button>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-6">
            {/* Course Header */}
            <Card className="p-6 mb-6 dark:bg-zinc-800">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">{course.name}</h1>
                <p className="text-zinc-600 dark:text-zinc-400 mb-4">{course.code}</p>
                
                {/* Progress Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <StatCard 
                        title="Overall Progress" 
                        value={`${progress?.percentage || 0}%`}
                        icon={ChartBarIcon}
                        color="text-blue-500"
                    />
                    <StatCard 
                        title="Completed Items" 
                        value={progress?.completed_items || 0}
                        icon={BookOpenIcon}
                        color="text-green-500"
                    />
                    <StatCard 
                        title="Total Items" 
                        value={progress?.total_items || 0}
                        icon={ClipboardDocumentListIcon}
                        color="text-purple-500"
                    />
                </div>

                <p className="text-zinc-700 dark:text-zinc-300">{course.description}</p>
            </Card>

            {/* Course Content */}
            <div className="space-y-6">
                {course.weeks && course.weeks.length > 0 ? (
                    course.weeks.map(week => {
                        const weekProgress = progress?.weeks?.find(w => w.week_id === week.id)?.progress || { percentage: 0 };
                        return (
                            <Card key={week.id} className="dark:bg-zinc-800">
                                <div className="p-6">
                                    <div className="flex justify-between items-center mb-4">
                                        <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                                            Week {week.number}: {week.title}
                                        </h2>
                                        <span className="text-sm text-zinc-600 dark:text-zinc-400">
                                            Progress: {weekProgress.percentage}%
                                        </span>
                                    </div>
                                    
                                    {/* Progress Bar */}
                                    <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-2 mb-4">
                                        <div 
                                            className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                                            style={{ width: `${weekProgress.percentage}%` }}
                                        />
                                    </div>

                                    <p className="text-zinc-600 dark:text-zinc-400 mb-6">{week.description}</p>

                                    {/* Lectures */}
                                    <div className="space-y-3">
                                        {week.lectures.map(lecture => (
                                            <div
                                                key={lecture.id}
                                                onClick={() => navigate(`/student/courses/${courseId}/week/${week.id}/lecture/${lecture.id}`)}
                                                className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-700 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-600 cursor-pointer transition-colors"
                                            >
                                                <div className="flex items-center">
                                                    {lecture.completed && (
                                                        <span className="mr-3 text-green-600 dark:text-green-500">
                                                            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                            </svg>
                                                        </span>
                                                    )}
                                                    <div>
                                                        <h4 className="font-medium text-zinc-900 dark:text-white">{lecture.title}</h4>
                                                        <p className="text-sm text-zinc-600 dark:text-zinc-400">{lecture.description}</p>
                                                    </div>
                                                </div>
                                                <svg className="h-5 w-5 text-zinc-400 dark:text-zinc-500" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                                </svg>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Assignments */}
                                    {week.assignments && week.assignments.length > 0 && (
                                        <div className="mt-6">
                                            <h3 className="text-lg font-medium mb-4 text-zinc-900 dark:text-white">Assignments</h3>
                                            <div className="space-y-3">
                                                {week.assignments.map(assignment => (
                                                    <div
                                                        key={assignment.id}
                                                        onClick={() => navigate(`/student/assignments/${assignment.id}`)}
                                                        className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-700 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-600 cursor-pointer transition-colors"
                                                    >
                                                        <div className="flex items-center">
                                                            {assignment.completed && (
                                                                <span className="mr-3 text-green-600 dark:text-green-500">
                                                                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                                    </svg>
                                                                </span>
                                                            )}
                                                            <div>
                                                                <h4 className="font-medium text-zinc-900 dark:text-white">{assignment.title}</h4>
                                                                <p className="text-sm text-zinc-600 dark:text-zinc-400">Due: {new Date(assignment.due_date).toLocaleDateString()}</p>
                                                            </div>
                                                        </div>
                                                        <svg className="h-5 w-5 text-zinc-400 dark:text-zinc-500" viewBox="0 0 20 20" fill="currentColor">
                                                            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                                        </svg>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </Card>
                        );
                    })
                ) : (
                    <Card className="text-center py-8 dark:bg-zinc-800">
                        <p className="text-zinc-600 dark:text-zinc-400">No content available for this course yet.</p>
                    </Card>
                )}
            </div>
        </div>
    );
};

export default CourseDetail; 