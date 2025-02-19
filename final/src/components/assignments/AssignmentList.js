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

    const assignments = Object.keys(assignmentData).map((key) => ({
        id: key,
        ...assignmentData[key],
    }));

    const filteredAssignments = assignments.filter(assignment => {
        return filters.type === 'All Types' || 
               assignment.type.toLowerCase() === filters.type.toLowerCase();
    });

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">
                        Assignments
                    </h1>
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                        View and manage your course assignments
                    </p>
                </div>

                {/* Filters */}
                <div className="flex gap-4">
                    <select
                        value={filters.type}
                        onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
                        className="px-4 py-2 text-sm bg-white/60 dark:bg-zinc-800/60 
                                 text-zinc-900 dark:text-white rounded-lg
                                 border border-zinc-200/50 dark:border-zinc-700/50
                                 focus:outline-none focus:ring-2 focus:ring-zinc-500/50 dark:focus:ring-zinc-400/50
                                 hover:bg-white dark:hover:bg-zinc-800 transition-all duration-200"
                    >
                        <option>All Types</option>
                        <option>Practice</option>
                        <option>Graded</option>
                    </select>
                </div>
            </div>

            {/* Assignments Table */}
            <div className="bg-white/60 dark:bg-zinc-800/60 rounded-xl overflow-hidden
                          shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                          dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                <table className="min-w-full divide-y divide-zinc-200 dark:divide-zinc-700/50">
                    <thead className="bg-zinc-50/80 dark:bg-zinc-900/50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                Course
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                Title
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                Type
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                Due Date
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                                Points
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-200 dark:divide-zinc-700/50">
                        {filteredAssignments.map(assignment => (
                            <tr
                                key={assignment.id}
                                onClick={() => navigate(`/assignments/${assignment.id}`)}
                                className="group hover:bg-zinc-50 dark:hover:bg-zinc-700/50 cursor-pointer transition-colors"
                            >
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium text-zinc-900 dark:text-white">
                                        {assignment.course}
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="text-sm text-zinc-600 dark:text-zinc-300">
                                        {assignment.title}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                                        ${assignment.type === 'graded' 
                                            ? 'bg-zinc-900 text-white dark:bg-white dark:text-zinc-900'
                                            : 'bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300'
                                        }`}>
                                        {assignment.type}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                        {assignment.due_date || 'No due date'}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-zinc-600 dark:text-zinc-300">
                                        {assignment.points_possible} pts
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {/* Empty State */}
                {filteredAssignments.length === 0 && (
                    <div className="text-center py-12">
                        <p className="text-zinc-500 dark:text-zinc-400">
                            No assignments found
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AssignmentList;