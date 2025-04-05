import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { 
    PencilSquareIcon, 
    TrashIcon, 
    PlusCircleIcon,
    ArrowLeftIcon,
    DocumentTextIcon,
    ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';

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
            console.log('Course content response:', response);
            
            if (response && response.success) {
                setCourse(response.data);
            } else {
                setError((response && response.message) || 'Failed to load course content');
                console.error('API error:', response);
            }
        } catch (err) {
            console.error('Error fetching course content:', err);
            setError('Failed to load course content. Please try again later.');
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

    const handleDeleteWeek = async (weekId) => {
        if (!window.confirm('Are you sure you want to delete this week and all its content? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await courseApi.deleteWeek(courseId, weekId);
            if (response.success) {
                // Refresh course content
                fetchCourseContent();
            } else {
                setError(response.message || 'Failed to delete week');
            }
        } catch (err) {
            console.error('Error deleting week:', err);
            setError('Failed to delete week');
        }
    };

    const navigateToWeekCreate = () => {
        navigate(`/ta/courses/${courseId}/weeks/new`);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4">
                    {error}
                </div>
                <div className="mt-4 text-center">
                    <button
                        onClick={() => navigate('/ta/courses')}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center justify-center gap-1"
                    >
                        <ArrowLeftIcon className="h-4 w-4" /> Back to Courses
                    </button>
                </div>
            </div>
        );
    }

    if (!course) {
        return (
            <div className="p-6">
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-400 rounded-lg p-4">
                    Course not found
                </div>
                <div className="mt-4 text-center">
                    <button
                        onClick={() => navigate('/ta/courses')}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center justify-center gap-1"
                    >
                        <ArrowLeftIcon className="h-4 w-4" /> Back to Courses
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <div>
                    <div className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                        <button
                            onClick={() => navigate('/ta/courses')}
                            className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"
                        >
                            <ArrowLeftIcon className="h-3 w-3" /> Courses
                        </button>
                        <span>→</span>
                        <span>{course.code}</span>
                    </div>
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">{course.name} - Content</h1>
                </div>
                <div className="flex space-x-2">
                    {/* <button
                        onClick={() => navigate(`/ta/courses/${courseId}/edit`)}
                        className="btn-secondary flex items-center space-x-1"
                    >
                        <PencilSquareIcon className="w-4 h-4" />
                        <span>Edit Course</span>
                    </button> */}
                    <button
                        onClick={navigateToWeekCreate}
                        className="btn-primary flex items-center space-x-1"
                    >
                        <PlusCircleIcon className="w-4 h-4" />
                        <span>Add Week</span>
                    </button>
                </div>
            </div>

            {/* Course Info */}
            <div className="glass-card p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">Course Description</h2>
                        <p className="text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">{course.description || 'No description available.'}</p>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Course Status</h3>
                            <span className={`px-2 py-1 text-sm rounded-full ${
                                course.is_active
                                    ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                                    : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400'
                            }`}>
                                {course.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Enrollment</h3>
                            <p className="text-zinc-900 dark:text-zinc-200">
                                {course.enrolled_count} students enrolled
                                {course.max_students ? ` (Max: ${course.max_students})` : ' (Unlimited)'}
                            </p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Teaching Assistants</h3>
                            <p className="text-zinc-900 dark:text-zinc-200">{course.teaching_assistants} TAs assigned</p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Created By</h3>
                            <p className="text-zinc-900 dark:text-zinc-200">{course.created_by}</p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Course Dates</h3>
                            <p className="text-zinc-900 dark:text-zinc-200">
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
                    <div key={week.id} className="glass-card">
                        <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
                                        Week {week.number}: {week.title}
                                    </h2>
                                    {week.description && (
                                        <p className="mt-1 text-zinc-600 dark:text-zinc-400">{week.description}</p>
                                    )}
                                </div>
                                <div className="flex space-x-2">
                                    <button
                                        onClick={() => navigate(`/ta/courses/${courseId}/weeks/${week.id}/edit`)}
                                        className="p-2 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white"
                                        title="Edit Week"
                                    >
                                        <PencilSquareIcon className="w-5 h-5" />
                                    </button>
                                    <button
                                        onClick={() => handleDeleteWeek(week.id)}
                                        className="p-2 text-zinc-600 dark:text-zinc-400 hover:text-red-600 dark:hover:text-red-400"
                                        title="Delete Week"
                                    >
                                        <TrashIcon className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                            <div className="mt-2 flex flex-wrap gap-2">
                                <span className={`px-2 py-1 text-xs rounded-full ${
                                    week.is_published
                                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                                        : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400'
                                }`}>
                                    {week.is_published ? 'Published' : 'Draft'}
                                </span>
                            </div>
                        </div>
                        <div className="p-6">
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg font-medium text-zinc-800 dark:text-zinc-200">Content</h3>
                                <div className="flex space-x-2">
                                    <button
                                        onClick={() => navigate(`/ta/courses/${courseId}/weeks/${week.id}/lectures/new`)}
                                        className="btn-secondary-sm flex items-center space-x-1"
                                    >
                                        <DocumentTextIcon className="w-4 h-4" />
                                        <span>Add Lecture</span>
                                    </button>
                                    <button
                                        onClick={() => navigate(`/ta/courses/${courseId}/weeks/${week.id}/assignments/new`)}
                                        className="btn-primary-sm flex items-center space-x-1"
                                    >
                                        <ClipboardDocumentListIcon className="w-4 h-4" />
                                        <span>Add Assignment</span>
                                    </button>
                                </div>
                            </div>

                            {/* Lectures */}
                            {week.lectures && week.lectures.length > 0 ? (
                                <div className="mb-6">
                                    <h4 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-2">Lectures</h4>
                                    <div className="space-y-2">
                                        {week.lectures.map(lecture => (
                                            <div key={lecture.id} className="flex justify-between items-center p-3 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                                                <div>
                                                    <h5 className="font-medium text-zinc-900 dark:text-white">{lecture.title}</h5>
                                                    {lecture.description && (
                                                        <p className="text-sm text-zinc-600 dark:text-zinc-400">{lecture.description}</p>
                                                    )}
                                                </div>
                                                <div className="flex space-x-1">
                                                    <button
                                                        onClick={() => navigate(`/ta/courses/${courseId}/weeks/${week.id}/lectures/${lecture.id}/edit`)}
                                                        className="p-1 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white"
                                                        title="Edit Lecture"
                                                    >
                                                        <PencilSquareIcon className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteLecture(lecture.id)}
                                                        className="p-1 text-zinc-600 dark:text-zinc-400 hover:text-red-600 dark:hover:text-red-400"
                                                        title="Delete Lecture"
                                                    >
                                                        <TrashIcon className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <div className="mb-6 p-4 bg-zinc-50 dark:bg-zinc-800 rounded-lg text-center text-zinc-600 dark:text-zinc-400">
                                    No lectures added yet
                                </div>
                            )}

                            {/* Assignments */}
                            {week.assignments && week.assignments.length > 0 ? (
                                <div>
                                    <h4 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-2">Assignments</h4>
                                    <div className="space-y-2">
                                        {week.assignments.map(assignment => (
                                            <div key={assignment.id} className="flex justify-between items-center p-3 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                                                <div>
                                                    <div className="flex items-center">
                                                        <h5 className="font-medium text-zinc-900 dark:text-white">{assignment.title}</h5>
                                                        <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                                                            assignment.type === 'graded'
                                                                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
                                                                : 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400'
                                                        }`}>
                                                            {assignment.type === 'graded' ? 'Graded' : 'Practice'}
                                                        </span>
                                                    </div>
                                                    {assignment.due_date && (
                                                        <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                                            Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                        </p>
                                                    )}
                                                </div>
                                                <div className="flex space-x-1">
                                                    <button
                                                        onClick={() => navigate(`/ta/assignments/${assignment.id}/edit`)}
                                                        className="p-1 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white"
                                                        title="Edit Assignment"
                                                    >
                                                        <PencilSquareIcon className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteAssignment(assignment.id)}
                                                        className="p-1 text-zinc-600 dark:text-zinc-400 hover:text-red-600 dark:hover:text-red-400"
                                                        title="Delete Assignment"
                                                    >
                                                        <TrashIcon className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <div className="p-4 bg-zinc-50 dark:bg-zinc-800 rounded-lg text-center text-zinc-600 dark:text-zinc-400">
                                    No assignments added yet
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {/* Empty state */}
                {(!course.weeks || course.weeks.length === 0) && (
                    <div className="glass-card p-8 text-center">
                        <p className="text-zinc-600 dark:text-zinc-400 mb-4">No weeks have been added to this course yet.</p>
                        <button
                            onClick={navigateToWeekCreate}
                            className="btn-primary inline-flex items-center space-x-2"
                        >
                            <PlusCircleIcon className="w-5 h-5" />
                            <span>Add First Week</span>
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseContent;