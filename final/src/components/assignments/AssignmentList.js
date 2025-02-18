import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const assignmentData = {
    301: {
        title: 'Practice Assignment 1.1',
        course: 'Introduction to Programming',
        type: 'practice',
        points_possible: 20,
        due_date: null
    },
    302: {
        title: 'Graded Assignment 1',
        course: 'Introduction to Programming',
        type: 'graded',
        points_possible: 50,
        due_date: '2025-03-01'
    },
    303: {
        title: 'Practice Assignment 2.1',
        course: 'Data Structures',
        type: 'practice',
        points_possible: 30,
        due_date: null
    }
};

const AssignmentList = () => {
    const navigate = useNavigate();
    const [filters, setFilters] = useState({ type: 'All Types' });

    // Convert assignmentData object into an array
    const assignments = Object.keys(assignmentData).map((key) => ({
        id: key,
        ...assignmentData[key],
    }));

    // Apply filters
    const filteredAssignments = assignments.filter(assignment => {
        return filters.type === 'All Types' || assignment.type.toLowerCase() === filters.type.toLowerCase();
    });

    return (
        <div className="container mx-auto p-6 bg-gray-900 text-white min-h-screen">
            <h1 className="text-3xl font-bold mb-2 text-yellow-400">My Assignments</h1>
            <p className="text-gray-400 mb-6">View and manage your course assignments</p>

            {/* Filters */}
            <div className="flex gap-8 mb-6">
                <div>
                    <label className="block mb-1 text-yellow-300">Type</label>
                    <select
                        value={filters.type}
                        onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
                        className="bg-gray-800 text-yellow-300 border border-yellow-500 rounded px-3 py-2 min-w-[150px]"
                    >
                        <option>All Types</option>
                        <option>Practice</option>
                        <option>Graded</option>
                    </select>
                </div>
            </div>

            {/* Assignments Table */}
            <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
                <table className="min-w-full text-white">
                    <thead className="bg-gray-700 text-yellow-300">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Course</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Title</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Due Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Points</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-600">
                        {filteredAssignments.length > 0 ? (
                            filteredAssignments.map(assignment => (
                                <tr
                                    key={assignment.id}
                                    className="hover:bg-gray-700 cursor-pointer"
                                    onClick={() => navigate(`/assignments/${assignment.id}`)}
                                >
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-semibold text-yellow-300">{assignment.course}</div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-sm font-medium">{assignment.title}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-3 py-1 text-xs font-semibold rounded-full ${assignment.type === 'practice'
                                            ? 'bg-green-700 text-green-300'
                                            : 'bg-blue-700 text-blue-300'
                                        }`}>
                                            {assignment.type.charAt(0).toUpperCase() + assignment.type.slice(1)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        {assignment.due_date ? new Date(assignment.due_date).toLocaleDateString() : 'No Due Date'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">{assignment.points_possible} pts</td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="5" className="text-center py-6 text-gray-400">
                                    No assignments found
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AssignmentList;
