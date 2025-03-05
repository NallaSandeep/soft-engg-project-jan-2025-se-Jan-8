import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import ReactMarkdown from 'react-markdown';
import { Card } from '../common/Card';

const CourseView = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeSection, setActiveSection] = useState('introduction');

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            setError(null);
            const response = await courseApi.getCourseContent(courseId);
            if (response.success) {
                setCourse(response.data);
            } else {
                setError(response.message || 'Failed to load course content');
            }
        } catch (err) {
            console.error('Error loading course content:', err);
            setError(err.message || 'Failed to load course content');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return (
        <div className="flex justify-center items-center h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading course content...</span>
        </div>
    );
    
    if (error) return (
        <div className="text-red-500 dark:text-red-400 text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            {error}
        </div>
    );
    
    if (!course) return (
        <div className="text-center p-4 text-zinc-600 dark:text-zinc-400">Course not found</div>
    );

    return (
        <div className="flex h-screen bg-zinc-50 dark:bg-zinc-900">
            {/* Left Sidebar - Course Structure */}
            <div className="w-64 bg-white dark:bg-zinc-800 shadow-lg dark:shadow-zinc-900/50 overflow-y-auto">
                <div className="p-4 border-b dark:border-zinc-700">
                    <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">{course.code}</h2>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400">{course.name}</p>
                </div>
                <nav className="p-2">
                    <button
                        onClick={() => setActiveSection('introduction')}
                        className={`w-full text-left p-2 rounded transition-colors ${
                            activeSection === 'introduction' 
                                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
                                : 'hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200'
                        }`}
                    >
                        Course Introduction
                    </button>
                    
                    {course.weeks?.map(week => (
                        <div key={week.id} className="mb-2">
                            <div className="p-2 bg-zinc-50 dark:bg-zinc-700 font-medium text-zinc-800 dark:text-zinc-200">
                                Week {week.number}: {week.title}
                            </div>
                            {week.lectures?.map(lecture => (
                                <button
                                    key={lecture.id}
                                    onClick={() => navigate(`/courses/${courseId}/lectures/${lecture.id}`)}
                                    className="w-full text-left p-2 pl-6 text-sm hover:bg-zinc-50 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-300 transition-colors"
                                >
                                    {lecture.title}
                                </button>
                            ))}
                            {week.assignments?.map(assignment => (
                                <button
                                    key={assignment.id}
                                    onClick={() => navigate(`/courses/${courseId}/assignments/${assignment.id}`)}
                                    className="w-full text-left p-2 pl-6 text-sm text-green-600 dark:text-green-500 hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors"
                                >
                                    📝 {assignment.title}
                                </button>
                            ))}
                        </div>
                    ))}
                </nav>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto p-6">
                {activeSection === 'introduction' ? (
                    <Card className="max-w-4xl mx-auto p-6 dark:bg-zinc-800">
                        <h1 className="text-3xl font-bold mb-4 text-zinc-900 dark:text-white">{course.name}</h1>
                        <div className="mb-6">
                            <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 px-3 py-1 rounded-full text-sm">
                                {course.code}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-6 mb-8">
                            <div>
                                <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">Course Faculty</h3>
                                <p className="text-zinc-600 dark:text-zinc-400">{course.created_by}</p>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-white">Course Duration</h3>
                                <p className="text-zinc-600 dark:text-zinc-400">
                                    {course.start_date} - {course.end_date}
                                </p>
                            </div>
                        </div>

                        <div className="prose dark:prose-invert max-w-none">
                            <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Course Description</h2>
                            <ReactMarkdown>{course.description}</ReactMarkdown>
                        </div>

                        <div className="mt-8">
                            <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-white">Course Structure</h2>
                            <div className="space-y-4">
                                {course.weeks?.map(week => (
                                    <div key={week.id} className="border dark:border-zinc-700 rounded-lg p-4 bg-white dark:bg-zinc-700/50">
                                        <h3 className="font-medium mb-2 text-zinc-900 dark:text-white">
                                            Week {week.number}: {week.title}
                                        </h3>
                                        <p className="text-zinc-600 dark:text-zinc-400 text-sm mb-2">{week.description}</p>
                                        <div className="pl-4">
                                            {week.lectures?.map(lecture => (
                                                <div key={lecture.id} className="text-sm py-1 text-zinc-800 dark:text-zinc-300">
                                                    • {lecture.title}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </Card>
                ) : null}
            </div>
        </div>
    );
};

export default CourseView; 