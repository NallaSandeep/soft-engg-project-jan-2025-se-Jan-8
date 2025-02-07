import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { assignmentApi } from '../../services/apiService';
import { useAuth } from '../../hooks/useAuth';

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
        return <div className="p-4">Loading assignments...</div>;
    }

    return (
        <div className="container mx-auto p-6">
            <h1 className="text-2xl font-bold mb-2">My Assignments</h1>
            <p className="text-gray-600 mb-4">View and manage your course assignments</p>

            {/* Filters */}
            <div className="flex gap-8 mb-6">
                <div>
                    <label className="block mb-1">Type</label>
                    <select
                        value={filters.type}
                        onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
                        className="border rounded px-3 py-1 min-w-[120px]"
                    >
                        <option>All Types</option>
                        <option>Practice</option>
                        <option>Graded</option>
                    </select>
                </div>
                <div>
                    <label className="block mb-1">Status</label>
                    <select
                        value={filters.status}
                        onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                        className="border rounded px-3 py-1 min-w-[120px]"
                    >
                        <option>All Status</option>
                        <option>Not Available</option>
                        <option>Available</option>
                    </select>
                </div>
            </div>

            {/* Assignments Table */}
            <div className="bg-white rounded-lg overflow-hidden">
                <table className="min-w-full">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Course
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Week
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Title
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Type
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Due Date
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Points
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {assignments.map(assignment => (
                            <tr
                                key={assignment.id}
                                className="hover:bg-gray-50 cursor-pointer"
                                onClick={() => navigate(`/courses/${assignment.course_id}/assignments/${assignment.id}`)}
                            >
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">{assignment.course_name}</div>
                                    <div className="text-sm text-gray-500">{assignment.course_code}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">Week {assignment.week_number}</div>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="text-sm font-medium text-gray-900">{assignment.title}</div>
                                    <div className="text-sm text-gray-500">{assignment.description}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${assignment.type === 'practice'
                                            ? 'bg-green-100 text-green-800'
                                            : 'bg-blue-100 text-blue-800'
                                        }`}>
                                        {assignment.type}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {new Date(assignment.due_date).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {assignment.points_possible} pts
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {assignments.length === 0 && (
                    <div className="text-center py-8 text-gray-600">
                        No assignments found
                    </div>
                )}
            </div>
        </div>
    );
};

export default AssignmentList; 