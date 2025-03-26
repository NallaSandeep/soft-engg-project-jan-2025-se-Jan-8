import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { assignmentApi } from '../../services/apiService';
import { Card } from '../common/Card';
import { ChevronRightIcon } from '@heroicons/react/24/outline';

const AssignmentList = () => {
    const navigate = useNavigate();
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
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
                <span className="ml-3 text-zinc-600 dark:text-zinc-400">Loading assignments...</span>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Card className="mb-8">
                <div className="p-4">
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">My Assignments</h1>
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">View and manage your course assignments</p>
                </div>
            </Card>

            {/* Filters */}
            <div className="mb-6 flex flex-wrap gap-4">
                <div className="min-w-[200px]">
                    <label className="block mb-1 text-sm font-medium text-zinc-700 dark:text-zinc-300">Type</label>
                    <select
                        value={filters.type}
                        onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
                        className="w-full rounded-lg border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm"
                    >
                        <option>All Types</option>
                        <option>Practice</option>
                        <option>Graded</option>
                    </select>
                </div>
                <div className="min-w-[200px]">
                    <label className="block mb-1 text-sm font-medium text-zinc-700 dark:text-zinc-300">Status</label>
                    <select
                        value={filters.status}
                        onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                        className="w-full rounded-lg border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-sm"
                    >
                        <option>All Status</option>
                        <option>Not Started</option>
                        <option>In Progress</option>
                        <option>Completed</option>
                    </select>
                </div>
            </div>

            <Card className="overflow-hidden dark:bg-zinc-800">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-zinc-200 dark:divide-zinc-700">
                        <thead>
                            <tr className="bg-zinc-50 dark:bg-zinc-700/50">
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Course
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Week
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Title
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Type
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Due Date
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                    Points
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-zinc-800 divide-y divide-zinc-200 dark:divide-zinc-700">
                            {assignments.map(assignment => (
                                <tr
                                    key={assignment.id}
                                    onClick={() => navigate(`/student/courses/${assignment.course_id}/assignments/${assignment.id}`)}
                                    className="hover:bg-zinc-50 dark:hover:bg-zinc-700/50 transition-colors cursor-pointer"
                                >
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-zinc-900 dark:text-white">{assignment.course_name}</div>
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
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                            assignment.type === 'practice'
                                                ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                                                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
                                        }`}>
                                            {assignment.type.charAt(0).toUpperCase() + assignment.type.slice(1)}
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
                        <div className="text-center py-12">
                            <p className="text-zinc-600 dark:text-zinc-400 text-sm">No assignments found</p>
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
};

export default AssignmentList; 