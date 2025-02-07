import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { assignmentApi, courseApi } from '../../../services/apiService';
import { useModal } from '../../common/Modal';

const AssignmentManagement = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const { showModal } = useModal();
    const [assignments, setAssignments] = useState([]);
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchData();
    }, [courseId]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [courseResponse, assignmentsResponse] = await Promise.all([
                courseApi.getCourse(courseId),
                assignmentApi.getCourseAssignments(courseId)
            ]);
            setCourse(courseResponse.data);
            setAssignments(assignmentsResponse.data || []);
        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Failed to load assignments');
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (assignment) => {
        navigate(`/admin/courses/${courseId}/weeks/${assignment.week_id}/assignments/${assignment.id}/edit`);
    };

    const handleDelete = async (assignment) => {
        showModal({
            title: 'Delete Assignment',
            content: (
                <div>
                    <p>Are you sure you want to delete "{assignment.title}"?</p>
                    <p className="text-sm text-gray-600 mt-2">
                        This action cannot be undone. All student submissions will also be deleted.
                    </p>
                </div>
            ),
            buttons: [
                {
                    label: 'Cancel',
                    variant: 'secondary'
                },
                {
                    label: 'Delete',
                    variant: 'danger',
                    onClick: async () => {
                        try {
                            await assignmentApi.deleteAssignment(assignment.id);
                            setAssignments(prev => prev.filter(a => a.id !== assignment.id));
                        } catch (err) {
                            console.error('Error deleting assignment:', err);
                            showModal({
                                title: 'Error',
                                content: 'Failed to delete assignment. Please try again.',
                                buttons: [{ label: 'OK' }]
                            });
                        }
                    }
                }
            ]
        });
    };

    const handleTogglePublish = async (assignment) => {
        try {
            const response = await assignmentApi.updateAssignment(assignment.id, {
                is_published: !assignment.is_published
            });
            setAssignments(prev => prev.map(a => 
                a.id === assignment.id ? { ...a, is_published: !a.is_published } : a
            ));
        } catch (err) {
            console.error('Error updating assignment:', err);
            showModal({
                title: 'Error',
                content: 'Failed to update assignment status. Please try again.',
                buttons: [{ label: 'OK' }]
            });
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-full">
                <div className="text-gray-600">Loading assignments...</div>
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
                    <span>{course?.name || 'Course'}</span>
                </div>
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900">Assignments</h1>
                    <button
                        onClick={() => navigate(`/admin/courses/${courseId}/weeks/new/assignments/new`)}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Create Assignment
                    </button>
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 mb-6">
                    {error}
                </div>
            )}

            <div className="space-y-4">
                {assignments.map(assignment => (
                    <div key={assignment.id} className="bg-white rounded-lg shadow">
                        <div className="p-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h2 className="text-lg font-semibold text-gray-900">
                                        {assignment.title}
                                    </h2>
                                    <p className="text-sm text-gray-600">
                                        Week {assignment.week_number} • {assignment.type === 'practice' ? 'Practice' : 'Graded'}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => handleTogglePublish(assignment)}
                                        className={`px-3 py-1 rounded-full text-sm ${
                                            assignment.is_published
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-yellow-100 text-yellow-800'
                                        }`}
                                    >
                                        {assignment.is_published ? 'Published' : 'Draft'}
                                    </button>
                                    <button
                                        onClick={() => handleEdit(assignment)}
                                        className="text-blue-600 hover:text-blue-800"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(assignment)}
                                        className="text-red-600 hover:text-red-800"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>

                            <p className="text-gray-600 mt-2">{assignment.description}</p>

                            <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-600">
                                <div>
                                    <span className="font-medium">Questions:</span>{' '}
                                    {assignment.questions?.length || 0}
                                </div>
                                <div>
                                    <span className="font-medium">Total Points:</span>{' '}
                                    {assignment.total_points}
                                </div>
                                <div>
                                    <span className="font-medium">Due:</span>{' '}
                                    {new Date(assignment.due_date).toLocaleDateString()}
                                </div>
                                {assignment.start_date && (
                                    <div>
                                        <span className="font-medium">Available from:</span>{' '}
                                        {new Date(assignment.start_date).toLocaleDateString()}
                                    </div>
                                )}
                            </div>

                            {assignment.submissions_count > 0 && (
                                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                                    <p className="text-blue-700">
                                        <span className="font-medium">Submissions:</span>{' '}
                                        {assignment.submissions_count} •{' '}
                                        <span className="font-medium">Average Score:</span>{' '}
                                        {assignment.average_score?.toFixed(1) || 'N/A'}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {assignments.length === 0 && (
                    <div className="bg-white rounded-lg shadow p-8 text-center">
                        <p className="text-gray-600">
                            No assignments found for this course.
                        </p>
                        <button
                            onClick={() => navigate(`/admin/courses/${courseId}/weeks/new/assignments/new`)}
                            className="text-blue-600 hover:text-blue-800 mt-2"
                        >
                            Create your first assignment
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AssignmentManagement; 