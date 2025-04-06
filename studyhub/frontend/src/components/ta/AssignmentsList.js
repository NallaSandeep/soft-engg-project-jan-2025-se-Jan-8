import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { assignmentApi, courseApi } from '../../services/apiService';
import { format } from 'date-fns';
import { 
    PencilSquareIcon, 
    TrashIcon, 
    EyeIcon, 
    PlusCircleIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';

const AssignmentsList = () => {
    const navigate = useNavigate();
    const [assignments, setAssignments] = useState([]);
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        course: '',
        status: '',
        search: ''
    });
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const itemsPerPage = 10;

    useEffect(() => {
        fetchData();
    }, [currentPage, filters]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [assignmentsResponse, coursesResponse] = await Promise.all([
                assignmentApi.getAssignments({
                    page: currentPage,
                    limit: itemsPerPage,
                    ...filters
                }),
                courseApi.getCourses()
            ]);

            // Process assignments to ensure week is properly formatted
            const processedAssignments = assignmentsResponse.data?.map(assignment => {
                // Handle the case where week is an object
                if (assignment.week && typeof assignment.week === 'object') {
                    return {
                        ...assignment,
                        weekNumber: assignment.week.number,
                        weekTitle: assignment.week.title
                    };
                }
                return assignment;
            }) || [];

            setAssignments(processedAssignments);
            setTotalPages(Math.ceil((assignmentsResponse.total || 0) / itemsPerPage));
            setCourses(coursesResponse.data || []);
        } catch (err) {
            console.error('Error fetching assignments:', err);
            setError('Failed to load assignments');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (assignmentId) => {
        if (window.confirm('Are you sure you want to delete this assignment?')) {
            try {
                const response = await assignmentApi.deleteAssignment(assignmentId);
                if (response.success) {
                    setAssignments(assignments.filter(a => a.id !== assignmentId));
                } else {
                    alert(response.message || 'Failed to delete assignment');
                }
            } catch (err) {
                console.error('Error deleting assignment:', err);
                alert('An error occurred while deleting the assignment');
            }
        }
    };

    const handleFilterChange = (name, value) => {
        setFilters({ ...filters, [name]: value });
        setCurrentPage(1); // Reset to first page when filters change
    };

    const handleRowClick = (assignmentId) => {
        navigate(`/ta/assignments/${assignmentId}`);
    };

    const handleEdit = (e, assignmentId) => {
        e.stopPropagation();
        navigate(`/ta/assignments/${assignmentId}/edit`);
    };

    const handleDeleteRow = async (e, assignmentId) => {
        e.stopPropagation();
        await handleDelete(assignmentId);
    };

    if (loading && assignments.length === 0) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading assignments...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded relative" role="alert">
                <strong className="font-bold">Error!</strong>
                <span className="block sm:inline"> {error}</span>
            </div>
        );
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Assignments</h1>
                <button
                    onClick={() => navigate('/ta/assignments/new')}
                    className="btn-primary flex items-center space-x-2"
                >
                    <PlusCircleIcon className="w-5 h-5" />
                    <span>Create Assignment</span>
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
                <div className="flex-1">
                    <input
                        type="text"
                        placeholder="Search assignments..."
                        value={filters.search}
                        onChange={(e) => handleFilterChange('search', e.target.value)}
                        className="input-field"
                    />
                </div>
                <div className="w-full md:w-48">
                    <select
                        value={filters.course}
                        onChange={(e) => handleFilterChange('course', e.target.value)}
                        className="input-field"
                    >
                        <option value="">All Courses</option>
                        {courses.map(course => (
                            <option key={course.id} value={course.id}>
                                {course.code} - {course.name}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="w-full md:w-48">
                    <select
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                        className="input-field"
                    >
                        <option value="">All Status</option>
                        <option value="published">Published</option>
                        <option value="draft">Draft</option>
                    </select>
                </div>
            </div>

            {/* Assignments Table */}
            <div className="glass-card overflow-hidden">
                <table className="min-w-full divide-y divide-zinc-200 dark:divide-zinc-700">
                    <thead className="bg-zinc-100 dark:bg-zinc-800">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">
                                Title
                            </th>
                            {/* <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">
                                Course
                            </th> */}
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">
                                Week
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">
                                Type
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">
                                Due Date
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">
                                Status
                            </th>
                            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-zinc-600 dark:text-zinc-400 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-zinc-0 dark:bg-zinc-900 divide-y divide-zinc-200 dark:divide-zinc-700">
                        {assignments.length > 0 ? (
                            assignments.map((assignment) => (
                                <tr 
                                    key={assignment.id} 
                                    onClick={() => handleRowClick(assignment.id)}
                                    className="hover:bg-zinc-50 dark:hover:bg-zinc-800 cursor-pointer transition-colors"
                                >
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400">
                                                <ClipboardDocumentListIcon className="h-6 w-6" />
                                            </div>
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-zinc-900 dark:text-white">
                                                    {assignment.title}
                                                </div>
                                                {/* <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                                    {assignment.points_possible} pts
                                                </div> */}
                                            </div>
                                        </div>
                                    </td>
                                    {/* <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-zinc-900 dark:text-white">
                                            {assignment.course?.code || 'N/A'}
                                        </div>
                                    </td> */}
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-zinc-900 dark:text-white">
                                            {assignment.weekNumber ? 
                                                `Week ${assignment.weekNumber}` : 
                                                (typeof assignment.week === 'object' ? 
                                                    `Week ${assignment.week.number}` : 
                                                    (assignment.week ? `Week ${assignment.week}` : 'N/A'))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                            assignment.type === 'practice' 
                                                ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400' 
                                                : 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400'
                                        }`}>
                                            {assignment.type.charAt(0).toUpperCase() + assignment.type.slice(1)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-zinc-900 dark:text-white">
                                            {assignment.dueDate ? format(new Date(assignment.dueDate), 'MMM d, yyyy') : 
                                             (assignment.due_date ? format(new Date(assignment.due_date), 'MMM d, yyyy') : 'N/A')}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                            (assignment.status === 'published' || assignment.is_published) 
                                                ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400' 
                                                : 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400'
                                        }`}>
                                            {assignment.status || (assignment.is_published ? 'Published' : 'Draft')}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <div className="flex justify-end space-x-2">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/ta/assignments/${assignment.id}`);
                                                }}
                                                className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                                                title="View Assignment"
                                            >
                                                <EyeIcon className="h-5 w-5" />
                                            </button>
                                            <button
                                                onClick={(e) => handleEdit(e, assignment.id)}
                                                className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300"
                                                title="Edit Assignment"
                                            >
                                                <PencilSquareIcon className="h-5 w-5" />
                                            </button>
                                            <button
                                                onClick={(e) => handleDeleteRow(e, assignment.id)}
                                                className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                                                title="Delete Assignment"
                                            >
                                                <TrashIcon className="h-5 w-5" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="7" className="px-6 py-4 text-center text-sm text-zinc-500 dark:text-zinc-400">
                                    No assignments found
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex justify-between items-center mt-6">
                    <div className="text-sm text-zinc-600 dark:text-zinc-400">
                        Page {currentPage} of {totalPages}
                    </div>
                    <div className="flex space-x-2">
                        <button
                            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                            disabled={currentPage === 1}
                            className={`p-2 rounded-lg ${
                                currentPage === 1
                                    ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-600 cursor-not-allowed'
                                    : 'bg-zinc-200 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-300 dark:hover:bg-zinc-600'
                            }`}
                        >
                            <ChevronLeftIcon className="h-5 w-5" />
                        </button>
                        <button
                            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                            disabled={currentPage === totalPages}
                            className={`p-2 rounded-lg ${
                                currentPage === totalPages
                                    ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-600 cursor-not-allowed'
                                    : 'bg-zinc-200 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-300 dark:hover:bg-zinc-600'
                            }`}
                        >
                            <ChevronRightIcon className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AssignmentsList; 