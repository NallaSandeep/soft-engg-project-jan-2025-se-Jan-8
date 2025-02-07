import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';

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

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="text-gray-600">Loading assignments...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-red-500 text-center p-4">{error}</div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold mb-8">Assignment Grading</h1>

            {/* Course Selection */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
                <h2 className="text-lg font-semibold mb-4">Select Course</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {courses.map(course => (
                        <button
                            key={course.id}
                            className={`p-4 rounded-lg border transition-all ${
                                selectedCourse?.id === course.id
                                    ? 'border-blue-500 bg-blue-50'
                                    : 'border-gray-200 hover:border-blue-300'
                            }`}
                            onClick={() => setSelectedCourse(course)}
                        >
                            <h3 className="font-medium">{course.name}</h3>
                            <p className="text-sm text-gray-600">{course.code}</p>
                        </button>
                    ))}
                </div>
            </div>

            {/* Pending Assignments */}
            <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                    <h2 className="text-xl font-semibold">
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
                                        className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                                    >
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="font-medium">{assignment.title}</h3>
                                                <p className="text-sm text-gray-600 mt-1">
                                                    Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <span className="inline-block px-3 py-1 text-sm rounded-full bg-yellow-100 text-yellow-800">
                                                    {assignment.submissions_count || 0} submissions
                                                </span>
                                            </div>
                                        </div>
                                        <div className="mt-4">
                                            <button
                                                className="text-blue-600 hover:text-blue-800"
                                                onClick={() => navigate(`/assignments/${assignment.id}/grade`)}
                                            >
                                                View Submissions →
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-600">
                                No assignments available for grading.
                            </div>
                        )
                    ) : (
                        <div className="text-center py-8 text-gray-600">
                            Select a course to view assignments.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AssignmentGrading; 