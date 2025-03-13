import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { assignmentApi, courseApi } from '../../services/apiService';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const AssignmentForm = ({ mode = 'create' }) => {
    const navigate = useNavigate();
    const { courseId, weekId, assignmentId } = useParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [assignmentData, setAssignmentData] = useState({
        title: '',
        description: '',
        type: 'practice', // practice or graded
        due_date: '',
        late_submission_penalty: 0,
        is_published: false
    });
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [week, setWeek] = useState(null);
    const [weeks, setWeeks] = useState([]);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                setError(null);

                // First, fetch all courses
                const coursesResponse = await courseApi.getCourses();
                if (!coursesResponse.success) {
                    throw new Error('Failed to load courses');
                }
                setCourses(coursesResponse.data);

                // If editing, fetch assignment data
                if (mode === 'edit' && assignmentId) {
                    const response = await assignmentApi.getAssignment(assignmentId);
                    if (response.success) {
                        const { data } = response;
                        setAssignmentData({
                            title: data.title,
                            description: data.description || '',
                            type: data.type,
                            due_date: data.due_date ? new Date(data.due_date).toISOString().split('T')[0] : '',
                            late_submission_penalty: data.late_submission_penalty || 0,
                            is_published: data.is_published
                        });
                        if (data.week) {
                            setWeek(data.week);
                            if (data.week.course) {
                                setSelectedCourse(data.week.course);
                                // Fetch weeks for this course
                                const weeksResponse = await courseApi.getWeeks(data.week.course.id);
                                if (weeksResponse.success) {
                                    setWeeks(weeksResponse.data);
                                }
                            }
                        }
                    } else {
                        throw new Error('Failed to load assignment');
                    }
                }
                
                // If creating from course content, load course and week data
                if (courseId) {
                    const courseResponse = await courseApi.getCourse(courseId);
                    if (courseResponse.success) {
                        setSelectedCourse(courseResponse.data);
                        
                        // Fetch weeks for this course
                        const weeksResponse = await courseApi.getWeeks(courseId);
                        if (weeksResponse.success) {
                            setWeeks(weeksResponse.data);
                            
                            // If weekId is provided, set the week
                            if (weekId) {
                                const selectedWeek = weeksResponse.data.find(w => w.id === parseInt(weekId));
                                if (selectedWeek) {
                                    setWeek(selectedWeek);
                                }
                            }
                        }
                    } else {
                        throw new Error('Failed to load course');
                    }
                }
            } catch (err) {
                console.error('Error loading data:', err);
                setError(err.message || 'Failed to load data');
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [mode, assignmentId, courseId, weekId]);

    const handleCourseChange = async (courseId) => {
        if (!courseId) {
            setSelectedCourse(null);
            setWeek(null);
            setWeeks([]);
            return;
        }

        try {
            const course = courses.find(c => c.id === parseInt(courseId));
            setSelectedCourse(course);
            setWeek(null);

            // Fetch weeks for this course
            const response = await courseApi.getWeeks(courseId);
            if (response.success) {
                setWeeks(response.data);
            } else {
                throw new Error('Failed to load weeks');
            }
        } catch (err) {
            console.error('Error loading weeks:', err);
            setError('Failed to load weeks for this course');
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setAssignmentData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!week) {
            setError('Please select a week');
            return;
        }

        try {
            setLoading(true);
            setError(null);

            const payload = {
                ...assignmentData,
                week_id: week.id
            };

            let response;
            if (mode === 'edit') {
                response = await assignmentApi.updateAssignment(assignmentId, payload);
            } else {
                response = await assignmentApi.createAssignment(week.id, payload);
            }

            if (response.success) {
                // Navigate back to course content or assignments list
                navigate(courseId 
                    ? `/admin/courses/${courseId}/content` 
                    : `/admin/courses/${selectedCourse.id}/content`);
            } else {
                throw new Error(response.message || `Failed to ${mode} assignment`);
            }
        } catch (err) {
            console.error(`Error ${mode}ing assignment:`, err);
            setError(`Failed to ${mode} assignment`);
        }
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
                        onClick={() => navigate(courseId ? `/admin/courses/${courseId}/content` : '/admin/assignments')}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center justify-center gap-1"
                    >
                        <ArrowLeftIcon className="h-4 w-4" /> Back
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                    <button
                        onClick={() => navigate(courseId ? `/admin/courses/${courseId}/content` : '/admin/assignments')}
                        className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"
                    >
                        <ArrowLeftIcon className="h-4 w-4" />
                        {courseId ? 'Course Content' : 'Assignments'}
                    </button>
                    <span>→</span>
                    <span>{mode === 'edit' ? 'Edit' : 'New'} Assignment</span>
                </div>
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                    {mode === 'edit' ? 'Edit' : 'Add New'} Assignment
                </h1>
            </div>

            <div className="glass-card p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Course Selection - Only show if not creating from course content */}
                    {!courseId && (
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Course
                            </label>
                            <select
                                className="input-field"
                                value={selectedCourse?.id || ''}
                                onChange={(e) => handleCourseChange(e.target.value)}
                                required
                            >
                                <option value="">Select Course</option>
                                {courses.map(course => (
                                    <option key={course.id} value={course.id}>
                                        {course.name} ({course.code})
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {/* Week Selection - Only show if course is selected and not creating from course content */}
                    {!weekId && selectedCourse && (
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Week
                            </label>
                            <select
                                className="input-field"
                                value={week?.id || ''}
                                onChange={(e) => {
                                    const selectedWeek = weeks.find(w => w.id === parseInt(e.target.value));
                                    setWeek(selectedWeek || null);
                                }}
                                required
                            >
                                <option value="">Select Week</option>
                                {weeks.map(week => (
                                    <option key={week.id} value={week.id}>
                                        Week {week.number}: {week.title}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Title
                        </label>
                        <input
                            type="text"
                            name="title"
                            value={assignmentData.title}
                            onChange={handleInputChange}
                            className="input-field"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Description
                        </label>
                        <textarea
                            name="description"
                            value={assignmentData.description}
                            onChange={handleInputChange}
                            rows={4}
                            className="input-field"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Type
                            </label>
                            <select
                                name="type"
                                value={assignmentData.type}
                                onChange={handleInputChange}
                                className="input-field"
                                required
                            >
                                <option value="practice">Practice</option>
                                <option value="graded">Graded</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Due Date
                            </label>
                            <input
                                type="date"
                                name="due_date"
                                value={assignmentData.due_date}
                                onChange={handleInputChange}
                                className="input-field"
                                required
                            />
                        </div>
                    </div>

                    {/* <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                                Late Submission Penalty (%)
                            </label>
                            <input
                                type="number"
                                name="late_submission_penalty"
                                value={assignmentData.late_submission_penalty}
                                onChange={handleInputChange}
                                min="0"
                                max="100"
                                className="input-field"
                            />
                        </div>

                        <div className="flex items-center h-full pt-6">
                            <label className="flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    name="is_published"
                                    checked={assignmentData.is_published}
                                    onChange={handleInputChange}
                                    className="h-4 w-4 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400 rounded"
                                />
                                <span className="ml-2 text-sm text-zinc-700 dark:text-zinc-300">
                                    Publish Assignment
                                </span>
                            </label>
                        </div>
                    </div> */}

                    <div className="flex justify-end space-x-4 pt-4">
                        <button
                            type="button"
                            onClick={() => navigate(courseId ? `/admin/courses/${courseId}/content` : '/admin/assignments')}
                            className="px-4 py-2 border border-zinc-300 dark:border-zinc-600 text-zinc-700 dark:text-zinc-300 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                        >
                            {mode === 'edit' ? 'Update' : 'Create'} Assignment
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AssignmentForm; 