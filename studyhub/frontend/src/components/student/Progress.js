import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

const Progress = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState({
        totalCourses: 0,
        completedCourses: 0,
        totalAssignments: 0,
        completedAssignments: 0,
        averageScore: 0
    });

    useEffect(() => {
        fetchProgress();
    }, []);

    const fetchProgress = async () => {
        try {
            setError(null);
            const response = await courseApi.getCourses();
            if (response.success) {
                const courses = response.data || [];
                setCourses(courses);

                // Calculate statistics
                let totalAssignments = 0;
                let completedAssignments = 0;
                let totalScore = 0;
                let scoreCount = 0;

                courses.forEach(course => {
                    course.weeks?.forEach(week => {
                        week.assignments?.forEach(assignment => {
                            totalAssignments++;
                            if (assignment.submitted) {
                                completedAssignments++;
                                if (assignment.score) {
                                    totalScore += (assignment.score / assignment.points_possible) * 100;
                                    scoreCount++;
                                }
                            }
                        });
                    });
                });

                setStats({
                    totalCourses: courses.length,
                    completedCourses: courses.filter(c => !c.is_active).length,
                    totalAssignments,
                    completedAssignments,
                    averageScore: scoreCount > 0 ? totalScore / scoreCount : 0
                });
            } else {
                setError(response.message || 'Failed to load progress');
            }
        } catch (err) {
            console.error('Error loading progress:', err);
            setError(err.message || 'Failed to load progress');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="flex justify-center items-center h-screen">Loading progress...</div>;
    if (error) return <div className="text-red-500 text-center p-4">{error}</div>;

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold mb-8">My Progress</h1>

            {/* Overall Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold mb-2">Course Progress</h3>
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-3xl font-bold text-blue-600">
                                {stats.completedCourses}/{stats.totalCourses}
                            </p>
                            <p className="text-sm text-gray-600">Courses Completed</p>
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
                                    strokeDasharray={`${(stats.completedCourses / stats.totalCourses) * 100}, 100`}
                                />
                            </svg>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold mb-2">Assignment Completion</h3>
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-3xl font-bold text-green-600">
                                {stats.completedAssignments}/{stats.totalAssignments}
                            </p>
                            <p className="text-sm text-gray-600">Assignments Completed</p>
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
                                    strokeDasharray={`${(stats.completedAssignments / stats.totalAssignments) * 100}, 100`}
                                />
                            </svg>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold mb-2">Average Score</h3>
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-3xl font-bold text-purple-600">
                                {stats.averageScore.toFixed(1)}%
                            </p>
                            <p className="text-sm text-gray-600">Overall Performance</p>
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
                                    stroke="#9333ea"
                                    strokeWidth="3"
                                    strokeDasharray={`${stats.averageScore}, 100`}
                                />
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            {/* Course-wise Progress */}
            <div className="space-y-6">
                <h2 className="text-xl font-semibold">Course-wise Progress</h2>
                {courses.map(course => (
                    <div key={course.id} className="bg-white rounded-lg shadow-sm p-6">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-semibold">{course.name}</h3>
                                <p className="text-sm text-gray-600">{course.code}</p>
                            </div>
                            <button
                                key={course.id}
                                onClick={() => navigate(`/student/courses/${course.id}`)}
                                className="w-full p-4 rounded-lg border border-zinc-200 dark:border-zinc-700 hover:border-blue-500 dark:hover:border-blue-500 bg-white dark:bg-zinc-800 transition-colors group"
                            >
                                View Course →
                            </button>
                        </div>
                        <div className="space-y-2">
                            <div>
                                <div className="flex justify-between text-sm text-gray-600 mb-1">
                                    <span>Course Progress</span>
                                    <span>0%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-gray-600">Start Date:</span>
                                    <span className="ml-2">{course.start_date}</span>
                                </div>
                                <div>
                                    <span className="text-gray-600">End Date:</span>
                                    <span className="ml-2">{course.end_date}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Progress; 