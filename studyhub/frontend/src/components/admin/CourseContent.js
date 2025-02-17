import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';

const CourseContent = () => {
    const navigate = useNavigate();
    const { courseId } = useParams();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            setLoading(true);
            const response = await courseApi.getCourseContent(courseId);
            if (response.success) {
                setCourse(response.data);
            } else {
                setError(response.message || 'Failed to load course content');
            }
        } catch (err) {
            console.error('Error fetching course content:', err);
            setError('Failed to load course content');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteLecture = async (lectureId) => {
        if (!window.confirm('Are you sure you want to delete this lecture? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await courseApi.deleteLecture(lectureId);
            if (response.success) {
                // Refresh course content
                fetchCourseContent();
            } else {
                setError(response.message || 'Failed to delete lecture');
            }
        } catch (err) {
            console.error('Error deleting lecture:', err);
            setError('Failed to delete lecture');
        }
    };

    const handleDeleteAssignment = async (assignmentId) => {
        if (!window.confirm('Are you sure you want to delete this assignment? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await courseApi.deleteAssignment(assignmentId);
            if (response.success) {
                // Refresh course content
                fetchCourseContent();
            } else {
                setError(response.message || 'Failed to delete assignment');
            }
        } catch (err) {
            console.error('Error deleting assignment:', err);
            setError('Failed to delete assignment');
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
            return;
        }

        try {
            await courseApi.deleteCourse(courseId);
            navigate('/admin/courses', { replace: true });
        } catch (err) {
            console.error('Error deleting course:', err);
            setError('Failed to delete course');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading course content...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4">
                    {error}
                </div>
            </div>
        );
    }

    if (!course) {
        return (
            <div className="p-6">
                <div className="bg-yellow-50 border border-yellow-200 text-yellow-600 rounded-lg p-4">
                    Course not found
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <button
                        onClick={() => navigate('/admin/courses')}
                        className="hover:text-blue-600"
                    >
                        Courses
                    </button>
                    <span>→</span>
                    <span>{course.name}</span>
                </div>
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">{course.name}</h1>
                        <p className="text-gray-600">{course.code}</p>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => navigate(`/admin/courses/${courseId}/edit`)}
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
                        >
                            <FaEdit /> Edit Course
                        </button>
                        <button
                            onClick={handleDelete}
                            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex items-center gap-2"
                        >
                            <FaTrash /> Delete Course
                        </button>
                    </div>
                </div>
            </div>

            {/* Course Information */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h2 className="text-lg font-semibold mb-4">Course Description</h2>
                        <p className="text-gray-700 whitespace-pre-wrap">{course.description || 'No description available.'}</p>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Course Status</h3>
                            <span className={`px-2 py-1 text-sm rounded-full ${
                                course.is_active
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-red-100 text-red-800'
                            }`}>
                                {course.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Enrollment</h3>
                            <p className="text-gray-900">
                                {course.enrolled_count} students enrolled
                                {course.max_students ? ` (Max: ${course.max_students})` : ' (Unlimited)'}
                            </p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Teaching Assistants</h3>
                            <p className="text-gray-900">{course.teaching_assistants} TAs assigned</p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Created By</h3>
                            <p className="text-gray-900">{course.created_by}</p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Course Dates</h3>
                            <p className="text-gray-900">
                                {course.start_date && course.end_date 
                                    ? `${new Date(course.start_date).toLocaleDateString()} - ${new Date(course.end_date).toLocaleDateString()}`
                                    : 'No dates set'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Weeks */}
            <div className="space-y-6">
                {course.weeks?.map((week, weekIndex) => (
                    <div key={week.id} className="bg-white rounded-lg shadow">
                        <div className="p-6 border-b border-gray-200">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h2 className="text-lg font-semibold">Week {week.number}: {week.title}</h2>
                                    <p className="text-gray-600 mt-1">{week.description}</p>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <div className="flex space-x-1">
                                        <button
                                            onClick={() => navigate(`/admin/courses/${courseId}/weeks/${week.id}/lectures/new`)}
                                            className="bg-blue-100 text-blue-700 px-3 py-2 rounded-lg hover:bg-blue-200 flex items-center gap-1"
                                            title="Add Lecture"
                                        >
                                            <FaPlus className="text-sm" /> Lecture
                                        </button>
                                        <button
                                            onClick={() => navigate(`/admin/courses/${courseId}/weeks/${week.id}/assignments/new`)}
                                            className="bg-green-100 text-green-700 px-3 py-2 rounded-lg hover:bg-green-200 flex items-center gap-1"
                                            title="Add Assignment"
                                        >
                                            <FaPlus className="text-sm" /> Assignment
                                        </button>
                                    </div>
                                    <button
                                        onClick={() => navigate(`/admin/courses/${courseId}/weeks/${week.id}/edit`)}
                                        className="text-gray-600 hover:text-blue-600 p-2 rounded-lg hover:bg-gray-100"
                                        title="Edit Week"
                                    >
                                        <FaEdit />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Lectures */}
                        <div className="p-4">
                            <h3 className="text-sm font-medium text-gray-700 mb-3">Lectures</h3>
                            <div className="space-y-3">
                                {week.lectures?.length > 0 ? (
                                    week.lectures.map(lecture => (
                                        <div key={lecture.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                            <div>
                                                <h4 className="font-medium">{lecture.title}</h4>
                                                <p className="text-sm text-gray-600">{lecture.description}</p>
                                            </div>
                                            <div className="flex space-x-2">
                                                <button
                                                    onClick={() => navigate(`/admin/courses/${courseId}/lectures/${lecture.id}/edit`)}
                                                    className="text-indigo-600 hover:text-indigo-900"
                                                    title="Edit Lecture"
                                                >
                                                    <FaEdit />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteLecture(lecture.id)}
                                                    className="text-red-600 hover:text-red-900"
                                                    title="Delete Lecture"
                                                >
                                                    <FaTrash />
                                                </button>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center py-4 text-gray-500">
                                        No lectures added yet
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Assignments */}
                        <div className="p-4 border-t border-gray-200">
                            <h3 className="text-sm font-medium text-gray-700 mb-3">Assignments</h3>
                            <div className="space-y-3">
                                {week.assignments?.length > 0 ? (
                                    week.assignments.map(assignment => (
                                        <div key={assignment.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                            <div>
                                                <h4 className="font-medium">{assignment.title}</h4>
                                                <p className="text-sm text-gray-600">Due: {new Date(assignment.due_date).toLocaleDateString()}</p>
                                            </div>
                                            <div className="flex space-x-2">
                                                <button
                                                    onClick={() => navigate(`/admin/assignments/${assignment.id}/edit`)}
                                                    className="text-indigo-600 hover:text-indigo-900"
                                                    title="Edit Assignment"
                                                >
                                                    <FaEdit />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteAssignment(assignment.id)}
                                                    className="text-red-600 hover:text-red-900"
                                                    title="Delete Assignment"
                                                >
                                                    <FaTrash />
                                                </button>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center py-4 text-gray-500">
                                        No assignments added yet
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Add Week Button */}
            <div className="mt-6">
                <button
                    onClick={() => navigate(`/admin/courses/${courseId}/weeks/new`)}
                    className="w-full py-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-500 transition-colors flex items-center justify-center gap-2"
                >
                    <FaPlus className="text-sm" /> Add New Week
                </button>
            </div>
        </div>
    );
};

export default CourseContent; 