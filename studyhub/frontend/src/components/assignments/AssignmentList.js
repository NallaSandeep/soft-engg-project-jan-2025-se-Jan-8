import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { assignmentApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';
import { Card } from '../common/Card';

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

    useEffect(() => {
        fetchAssignments();
    }, [filters]);

    const fetchAssignments = async () => {
        try {
            setLoading(true);
            const response = await assignmentApi.getAssignments(filters);
            setAssignments(response.data || []);
        } catch (err) {
            console.error('Error fetching assignments:', err);
            setError('Failed to load assignments');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="p-4 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading assignments...</span>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6">
            <h1 className="text-2xl font-bold mb-2 text-zinc-900 dark:text-white">My Assignments</h1>
            <p className="text-zinc-600 dark:text-zinc-400 mb-4">View and manage your course assignments</p>

            {/* Filters */}
            <div className="flex gap-8 mb-6">
                <div>
                    <label className="block mb-1 text-zinc-700 dark:text-zinc-300">Type</label>
                    <select
                        value={filters.type}
                        onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
                        className="border dark:border-zinc-600 rounded px-3 py-1 min-w-[120px] bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                    >
                        <option>All Types</option>
                        <option>Practice</option>
                        <option>Graded</option>
                    </select>
                </div>
                <div>
                    <label className="block mb-1 text-zinc-700 dark:text-zinc-300">Status</label>
                    <select
                        value={filters.status}
                        onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                        className="border dark:border-zinc-600 rounded px-3 py-1 min-w-[120px] bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                    >
                        <option>All Status</option>
                        <option>Not Available</option>
                        <option>Available</option>
                    </select>
                </div>
            </div>

            {/* Assignments Table */}
            <Card className="overflow-hidden dark:bg-zinc-800">
                <table className="min-w-full">
                    <thead className="bg-zinc-50 dark:bg-zinc-700">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-300 uppercase tracking-wider">
                                Course
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-300 uppercase tracking-wider">
                                Week
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-300 uppercase tracking-wider">
                                Title
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-300 uppercase tracking-wider">
                                Type
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-300 uppercase tracking-wider">
                                Due Date
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-300 uppercase tracking-wider">
                                Points
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-zinc-800 divide-y divide-zinc-200 dark:divide-zinc-700">
                        {assignments.map(assignment => (
                            <tr
                                key={assignment.id}
                                className="hover:bg-zinc-50 dark:hover:bg-zinc-700 cursor-pointer transition-colors"
                                onClick={() => navigate(`/courses/${assignment.course_id}/assignments/${assignment.id}`)}
                            >
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-zinc-900 dark:text-white">{assignment.course_name}</div>
                                    <div className="text-sm text-zinc-500 dark:text-zinc-400">{assignment.course_code}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-zinc-900 dark:text-white">Week {assignment.week_number}</div>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="text-sm font-medium text-zinc-900 dark:text-white">{assignment.title}</div>
                                    <div className="text-sm text-zinc-500 dark:text-zinc-400">{assignment.description}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                        assignment.type === 'practice'
                                            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                                            : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
                                    }`}>
                                        {assignment.type}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-500 dark:text-zinc-400">
                                    {new Date(assignment.due_date).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-500 dark:text-zinc-400">
                                    {assignment.points_possible} pts
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {assignments.length === 0 && (
                    <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
                        No assignments found
                    </div>
                )}
            </Card>
        </div>
    );
};

export default AssignmentList; 