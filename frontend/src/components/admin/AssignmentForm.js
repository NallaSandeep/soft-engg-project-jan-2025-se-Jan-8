import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { assignmentApi, courseApi } from '../../services/apiService';

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
                            // Find and set the course
                            const course = coursesResponse.data.find(c => c.id === data.week.course_id);
                            if (course) {
                                setSelectedCourse(course);
                                // Fetch weeks for this course
                                const courseContent = await courseApi.getCourseContent(course.id);
                                if (courseContent.success) {
                                    setWeeks(courseContent.data.weeks);
                                }
                            }
                        }
                    } else {
                        setError(response.message || 'Failed to load assignment data');
                    }
                }

                // If we have a specific weekId and courseId, fetch that week's data
                if (weekId && courseId) {
                    const courseResponse = await courseApi.getCourseContent(courseId);
                    if (courseResponse.success) {
                        const weekData = courseResponse.data.weeks.find(w => w.id === parseInt(weekId));
                        if (weekData) {
                            setWeek(weekData);
                            setSelectedCourse(courseResponse.data);
                            setWeeks(courseResponse.data.weeks);
                        }
                    }
                }
            } catch (err) {
                console.error('Error loading data:', err);
                setError('Failed to load data');
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [mode, assignmentId, weekId, courseId]);

    // Handle course selection
    const handleCourseChange = async (courseId) => {
        try {
            setWeek(null);
            if (!courseId) {
                setSelectedCourse(null);
                setWeeks([]);
                return;
            }

            const course = courses.find(c => c.id === parseInt(courseId));
            setSelectedCourse(course);

            // Fetch weeks for selected course
            const response = await courseApi.getCourseContent(courseId);
            if (response.success) {
                setWeeks(response.data.weeks);
            } else {
                setError('Failed to load weeks for selected course');
            }
        } catch (err) {
            console.error('Error loading course weeks:', err);
            setError('Failed to load course weeks');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (!selectedCourse) {
                setError('Please select a course');
                return;
            }
            if (!week && !weekId) {
                setError('Please select a week');
                return;
            }

            const submitData = {
                ...assignmentData,
                week_id: weekId || week.id
            };

            let response;
            if (mode === 'edit') {
                response = await assignmentApi.updateAssignment(assignmentId, submitData);
            } else {
                response = await assignmentApi.createAssignment(weekId || week.id, submitData);
            }

            if (response.success) {
                if (courseId) {
                    navigate(`/admin/courses/${courseId}/content`);
                } else {
                    navigate('/admin/assignments');
                }
            } else {
                setError(response.message || `Failed to ${mode} assignment`);
            }
        } catch (err) {
            console.error(`Error ${mode}ing assignment:`, err);
            setError(`Failed to ${mode} assignment`);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4">
                    {error}
                </div>
                <div className="mt-4 text-center">
                    <button
                        onClick={() => navigate(courseId ? `/admin/courses/${courseId}/content` : '/admin/assignments')}
                        className="text-blue-600 hover:text-blue-800"
                    >
                        ← Back
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <button
                        onClick={() => navigate(courseId ? `/admin/courses/${courseId}/content` : '/admin/assignments')}
                        className="hover:text-blue-600"
                    >
                        {courseId ? 'Course Content' : 'Assignments'}
                    </button>
                    <span>→</span>
                    <span>{mode === 'edit' ? 'Edit' : 'New'} Assignment</span>
                </div>
                <h1 className="text-2xl font-bold text-gray-900">
                    {mode === 'edit' ? 'Edit' : 'Add New'} Assignment
                </h1>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Course Selection - Only show if not creating from course content */}
                    {!courseId && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Course
                            </label>
                            <select
                                className="w-full border border-gray-300 rounded-lg px-3 py-2"
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
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Week
                            </label>
                            <select
                                className="w-full border border-gray-300 rounded-lg px-3 py-2"
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
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Title
                        </label>
                        <input
                            type="text"
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            value={assignmentData.title}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, title: e.target.value }))}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Description
                        </label>
                        <textarea
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            rows="4"
                            value={assignmentData.description}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, description: e.target.value }))}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Type
                        </label>
                        <select
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            value={assignmentData.type}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, type: e.target.value }))}
                            required
                        >
                            <option value="practice">Practice</option>
                            <option value="graded">Graded</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Due Date
                        </label>
                        <input
                            type="date"
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            value={assignmentData.due_date}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, due_date: e.target.value }))}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Late Submission Penalty (%)
                        </label>
                        <input
                            type="number"
                            min="0"
                            max="100"
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            value={assignmentData.late_submission_penalty}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, late_submission_penalty: parseFloat(e.target.value) || 0 }))}
                        />
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="is_published"
                            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                            checked={assignmentData.is_published}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, is_published: e.target.checked }))}
                        />
                        <label htmlFor="is_published" className="ml-2 block text-sm text-gray-900">
                            Published
                        </label>
                    </div>

                    <div className="flex justify-end space-x-3">
                        <button
                            type="button"
                            onClick={() => navigate(courseId ? `/admin/courses/${courseId}/content` : '/admin/assignments')}
                            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
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