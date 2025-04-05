import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import { 
    PlusCircleIcon, 
    AcademicCapIcon,
    PencilSquareIcon,
    DocumentTextIcon,
    ArrowLeftIcon,
    TrashIcon,
    EyeIcon,
    EyeSlashIcon,
    ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';

const CourseContentManagement = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeWeek, setActiveWeek] = useState(null);

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            setLoading(true);
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

    const handleDeleteWeek = async (weekId) => {
        if (!window.confirm('Are you sure you want to delete this week?')) return;
        try {
            await courseApi.deleteWeek(courseId, weekId);
            fetchCourseContent();
        } catch (err) {
            console.error('Error deleting week:', err);
            setError('Failed to delete week');
        }
    };

    const ActionButton = ({ label, icon: Icon, onClick, color = 'blue' }) => {
        const colorClasses = {
            blue: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white',
            green: 'bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-700 dark:hover:bg-emerald-600 text-white',
            red: 'bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-600 text-white',
            gray: 'bg-zinc-600 hover:bg-zinc-700 dark:bg-zinc-700 dark:hover:bg-zinc-600 text-white'
        };
    
        return (
            <button
                onClick={onClick}
                className={`flex items-center justify-center space-x-2 px-4 py-2 rounded-lg ${colorClasses[color]} shadow-sm hover:shadow-md transition-shadow text-sm`}
            >
                <Icon className="w-4 h-4" />
                <span>{label}</span>
            </button>
        );
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading course content...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Error!</strong>
                    <span className="block sm:inline"> {error}</span>
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
                <div className="bg-yellow-100 dark:bg-yellow-900/20 border border-yellow-400 dark:border-yellow-800 text-yellow-700 dark:text-yellow-400 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Course not found!</strong>
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
        <div className="space-y-6">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                    <button
                        onClick={() => navigate('/ta/courses')}
                        className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"
                    >
                        <ArrowLeftIcon className="h-3 w-3" /> Courses
                    </button>
                    <span>→</span>
                    <span>{course.name}</span>
                </div>
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Course Content Management</h1>
                    <ActionButton
                        label="Add Week"
                        icon={PlusCircleIcon}
                        onClick={() => navigate(`/ta/courses/${courseId}/weeks/new`)}
                        color="green"
                    />
                </div>
            </div>

            {/* Course Info Card */}
            <div className="glass-card p-6 mb-6">
                <div className="flex items-start gap-3">
                    <AcademicCapIcon className="w-6 h-6 text-blue-500 dark:text-blue-400 mt-1" />
                    <div>
                        <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">{course.name}</h2>
                        <p className="text-zinc-600 dark:text-zinc-400">{course.code}</p>
                        <p className="text-zinc-700 dark:text-zinc-300 my-3">{course.description}</p>
                        <div className="flex flex-wrap gap-3 text-sm">
                            <span className="flex items-center gap-1 text-zinc-600 dark:text-zinc-400">
                                <span>Enrollment:</span>
                                <span className={`px-2 py-0.5 rounded-full text-xs ${
                                    course.enrollment_type === 'open'
                                        ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400'
                                        : course.enrollment_type === 'closed'
                                            ? 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400'
                                            : 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400'
                                }`}>
                                    {course.enrollment_type}
                                </span>
                            </span>
                            <span className="text-zinc-600 dark:text-zinc-400">
                                Students: {course.enrolled_count || 0}/{course.max_students || 'Unlimited'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Weeks List */}
            <div className="space-y-6">
                {course.weeks?.length > 0 ? (
                    course.weeks.map((week, index) => (
                        <div
                            key={week.id}
                            className="glass-card hover:shadow-lg transition-shadow"
                        >
                            <div className="p-6 border-b border-zinc-200 dark:border-zinc-700">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">
                                            Week {index + 1}: {week.title}
                                        </h2>
                                        <p className="text-zinc-600 dark:text-zinc-400 mt-1">{week.description}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => setActiveWeek(activeWeek === week.id ? null : week.id)}
                                            className="flex items-center justify-center p-2 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white bg-zinc-100 dark:bg-zinc-800 rounded-lg"
                                        >
                                            {activeWeek === week.id ? (
                                                <><EyeSlashIcon className="w-4 h-4 mr-1" /> Hide Content</>
                                            ) : (
                                                <><EyeIcon className="w-4 h-4 mr-1" /> Show Content</>
                                            )}
                                        </button>
                                        <button
                                            onClick={() => navigate(`/ta/courses/${courseId}/weeks/${week.id}/edit`)}
                                            className="flex items-center justify-center p-2 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 bg-zinc-100 dark:bg-zinc-800 rounded-lg"
                                        >
                                            <PencilSquareIcon className="w-4 h-4 mr-1" /> Edit
                                        </button>
                                        <button
                                            onClick={() => handleDeleteWeek(week.id)}
                                            className="flex items-center justify-center p-2 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 bg-red-50 dark:bg-red-900/20 rounded-lg"
                                        >
                                            <TrashIcon className="w-4 h-4 mr-1" /> Delete
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {activeWeek === week.id && (
                                <div className="p-6 bg-zinc-50 dark:bg-zinc-800/50">
                                    <div className="space-y-6">
                                        {/* Lectures */}
                                        <div>
                                            <div className="flex justify-between items-center mb-3">
                                                <h3 className="font-medium text-zinc-900 dark:text-white">Lectures</h3>
                                                <ActionButton
                                                    label="Add Lecture"
                                                    icon={DocumentTextIcon}
                                                    onClick={() => navigate(`/ta/courses/${courseId}/weeks/${week.id}/lectures/new`)}
                                                    color="blue"
                                                />
                                            </div>
                                            {week.lectures?.length > 0 ? (
                                                <div className="space-y-2">
                                                    {week.lectures.map(lecture => (
                                                        <div
                                                            key={lecture.id}
                                                            className="flex justify-between items-center p-3 bg-white dark:bg-zinc-800 rounded-lg shadow-sm hover:shadow-md transition-shadow"
                                                        >
                                                            <span className="text-zinc-900 dark:text-white">{lecture.title}</span>
                                                            <ActionButton
                                                                label="Edit"
                                                                icon={PencilSquareIcon}
                                                                onClick={() => navigate(`/ta/courses/${courseId}/lectures/${lecture.id}/edit`)}
                                                                color="gray"
                                                            />
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="text-zinc-500 dark:text-zinc-400 p-3 bg-white dark:bg-zinc-800 rounded-lg text-center">No lectures added yet</p>
                                            )}
                                        </div>

                                        {/* Assignments */}
                                        <div>
                                            <div className="flex justify-between items-center mb-3">
                                                <h3 className="font-medium text-zinc-900 dark:text-white">Assignments</h3>
                                                <ActionButton
                                                    label="Add Assignment"
                                                    icon={ClipboardDocumentListIcon}
                                                    onClick={() => navigate(`/ta/courses/${courseId}/weeks/${week.id}/assignments/new`)}
                                                    color="green"
                                                />
                                            </div>
                                            {week.assignments?.length > 0 ? (
                                                <div className="space-y-2">
                                                    {week.assignments.map(assignment => (
                                                        <div
                                                            key={assignment.id}
                                                            className="flex justify-between items-center p-3 bg-white dark:bg-zinc-800 rounded-lg shadow-sm hover:shadow-md transition-shadow"
                                                        >
                                                            <div>
                                                                <span className="text-zinc-900 dark:text-white">{assignment.title}</span>
                                                                {assignment.due_date && (
                                                                    <p className="text-xs text-zinc-500 dark:text-zinc-400">
                                                                        Due: {new Date(assignment.due_date).toLocaleDateString()}
                                                                    </p>
                                                                )}
                                                            </div>
                                                            <ActionButton
                                                                label="Edit"
                                                                icon={PencilSquareIcon}
                                                                onClick={() => navigate(`/ta/assignments/${assignment.id}/edit`)}
                                                                color="gray"
                                                            />
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="text-zinc-500 dark:text-zinc-400 p-3 bg-white dark:bg-zinc-800 rounded-lg text-center">No assignments added yet</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <div className="glass-card p-8 text-center">
                        <AcademicCapIcon className="w-12 h-12 text-zinc-400 dark:text-zinc-500 mx-auto mb-4" />
                        <p className="text-zinc-600 dark:text-zinc-400">No weeks added to this course yet.</p>
                        <p className="text-sm text-zinc-500 dark:text-zinc-500 mt-2 mb-4">
                            Add weeks to organize your course content.
                        </p>
                        <button
                            onClick={() => navigate(`/ta/courses/${courseId}/weeks/new`)}
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

export default CourseContentManagement;