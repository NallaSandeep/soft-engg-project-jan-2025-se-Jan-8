import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { assignmentApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';
import { Card } from '../common/Card';
import { 
    CheckCircleIcon, 
    ClockIcon, 
    XCircleIcon,
    AcademicCapIcon,
    BeakerIcon,
    CalendarIcon,
    ClipboardDocumentCheckIcon
} from '@heroicons/react/24/outline';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/20/solid';

const AssignmentList = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        type: 'All Types',
        status: 'All Status'
    });
    const [pagination, setPagination] = useState({
        page: 1,
        per_page: 9,
        total: 0,
        pages: 0
    });

    useEffect(() => {
        fetchAssignments();
    }, [filters, pagination.page]);

    const fetchAssignments = async () => {
        try {
            setLoading(true);
            const response = await assignmentApi.getAssignments({
                ...filters,
                type: filters.type !== 'All Types' ? filters.type.toLowerCase() : undefined,
                status: filters.status !== 'All Status' ? filters.status.toLowerCase() : undefined,
                page: pagination.page,
                limit: pagination.per_page
            });
            
            if (response.success) {
                let filteredAssignments = response.data || [];
                
                // Apply status filter on client side if needed
                if (filters.status !== 'All Status') {
                    filteredAssignments = filteredAssignments.filter(assignment => {
                        const { status } = getAssignmentStatus(assignment);
                        return status.toLowerCase() === filters.status.toLowerCase();
                    });
                }
                
                setAssignments(filteredAssignments);
                setPagination({
                    ...pagination,
                    total: filteredAssignments.length,
                    pages: Math.ceil(filteredAssignments.length / pagination.per_page)
                });
            } else {
                setError(response.message || 'Failed to load assignments');
            }
        } catch (err) {
            console.error('Error fetching assignments:', err);
            setError('Failed to load assignments');
        } finally {
            setLoading(false);
        }
    };

    const getAssignmentStatus = (assignment) => {
        const now = new Date();
        const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;
        const submission = assignment.submission;

        if (dueDate && now > dueDate && !submission) {
            return { status: 'overdue', icon: XCircleIcon, color: 'text-red-500 dark:text-red-400' };
        } else if (submission) {
            return { status: 'completed', icon: CheckCircleIcon, color: 'text-green-500 dark:text-green-400' };
        } else {
            return { status: 'not submitted', icon: ClockIcon, color: 'text-yellow-500 dark:text-yellow-400' };
        }
    };

    const handlePageChange = (newPage) => {
        if (newPage >= 1 && newPage <= pagination.pages) {
            setPagination(prev => ({ ...prev, page: newPage }));
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'No due date';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
    };

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-red-500 dark:text-red-400 text-center">{error}</div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Assignments</h1>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">Track and manage your course assignments</p>
                </div>
                <div className="flex gap-4 w-full md:w-auto">
                    <select
                        className="w-full md:w-40 rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 
                                 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:ring-2 focus:ring-blue-500
                                 [&>option]:bg-white [&>option]:dark:bg-gray-800 [&>option]:text-gray-900 [&>option]:dark:text-white"
                        value={filters.type}
                        onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
                    >
                        <option>All Types</option>
                        <option>Practice</option>
                        <option>Graded</option>
                    </select>
                    <select
                        className="w-full md:w-40 rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 
                                 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:ring-2 focus:ring-blue-500
                                 [&>option]:bg-white [&>option]:dark:bg-gray-800 [&>option]:text-gray-900 [&>option]:dark:text-white"
                        value={filters.status}
                        onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                    >
                        <option>All Status</option>
                        <option>Not Submitted</option>
                        <option>Completed</option>
                        <option>Overdue</option>
                    </select>
                </div>
            </div>

            <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                {assignments.map((assignment) => {
                    const { status, icon: StatusIcon, color } = getAssignmentStatus(assignment);
                    const TypeIcon = assignment.type === 'graded' ? AcademicCapIcon : BeakerIcon;
                    const typeColor = assignment.type === 'graded' 
                        ? 'text-purple-500 dark:text-purple-400' 
                        : 'text-blue-500 dark:text-blue-400';

                    return (
                        <Card
                            key={assignment.id}
                            onClick={() => navigate(`/student/courses/${assignment.week.course_id}/assignments/${assignment.id}`)}
                            className="cursor-pointer hover:shadow-lg transition-shadow bg-white dark:bg-gray-800"
                        >
                            <div className="p-4 flex flex-col h-full">
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center gap-2">
                                        <TypeIcon className={`h-6 w-6 ${typeColor}`} />
                                        <span className={`text-sm font-medium capitalize ${typeColor}`}>
                                            {assignment.type}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <StatusIcon className={`h-6 w-6 ${color}`} />
                                        <span className={`text-sm font-medium capitalize ${color}`}>{status}</span>
                                    </div>
                                </div>

                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                                    {assignment.title}
                                </h3>

                                <div className="flex-grow space-y-2">
                                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                                        <CalendarIcon className="h-5 w-5" />
                                        <span className="text-sm">Due: {formatDate(assignment.due_date)}</span>
                                    </div>

                                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                                        <ClipboardDocumentCheckIcon className="h-5 w-5" />
                                        <span className="text-sm">
                                            Score: {assignment.submission ? `${assignment.submission.score}/${assignment.points_possible}` : 'Not yet submitted'}
                                        </span>
                                    </div>
                                </div>

                                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        {assignment.submission 
                                            ? `Submitted: ${formatDate(assignment.submission.submitted_at)}`
                                            : 'Not yet submitted'}
                                    </p>
                                </div>
                            </div>
                        </Card>
                    );
                })}
            </div>

            {assignments.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-gray-600 dark:text-gray-400">No assignments found</p>
                </div>
            )}

            {pagination.pages > 1 && (
                <div className="flex justify-center items-center gap-4 mt-8">
                    <button
                        onClick={() => handlePageChange(pagination.page - 1)}
                        disabled={pagination.page === 1}
                        className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 text-gray-700 dark:text-gray-300"
                    >
                        <ChevronLeftIcon className="h-5 w-5" />
                    </button>
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                        Page {pagination.page} of {pagination.pages}
                    </span>
                    <button
                        onClick={() => handlePageChange(pagination.page + 1)}
                        disabled={pagination.page === pagination.pages}
                        className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 text-gray-700 dark:text-gray-300"
                    >
                        <ChevronRightIcon className="h-5 w-5" />
                    </button>
                </div>
            )}
        </div>
    );
};

export default AssignmentList; 