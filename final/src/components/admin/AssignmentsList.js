import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { PencilIcon, TrashIcon, EyeIcon } from '@heroicons/react/24/outline';

const mockAssignments = [
    {
        id: 1,
        course: { name: 'Introduction to Programming', code: 'CS101' },
        week: { number: 1, title: 'Week 1' },
        title: 'Practice Assignment 1.1',
        type: 'practice',
        due_date: '2025-01-31',
        points_possible: 4,
        is_published: true,
    },
    {
        id: 2,
        course: { name: 'Introduction to Programming', code: 'CS101' },
        week: { number: 1, title: 'Week 1' },
        title: 'Graded Assignment 1',
        type: 'graded',
        due_date: '2025-01-31',
        points_possible: 4,
        is_published: true,
    },
    {
        id: 3,
        course: { name: 'Introduction to Programming', code: 'CS101' },
        week: { number: 2, title: 'Week 2' },
        title: 'Practice Assignment 2.1',
        type: 'practice',
        due_date: '2025-02-07',
        points_possible: 4,
        is_published: true,
    },
];

const AssignmentsList = () => {
    const navigate = useNavigate();
    const [assignments, setAssignments] = useState(mockAssignments);

    const handleRowClick = (assignmentId) => {
        navigate(`/admin/assignments/${assignmentId}`);
    };

    const handleEdit = (e, assignmentId) => {
        e.stopPropagation();
        navigate(`/admin/assignments/${assignmentId}/edit`);
    };

    const handleDeleteRow = (e, assignmentId) => {
        e.stopPropagation();
        if (window.confirm('Are you sure you want to delete this assignment?')) {
            setAssignments((prev) => prev.filter((a) => a.id !== assignmentId));
        }
    };

    return (
        <div className="p-6 bg-gray-900 text-yellow-400 min-h-screen">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-yellow-400">Assignments</h1>
                <button
                    onClick={() => navigate('/admin/assignments/new')}
                    className="bg-yellow-500 text-gray-900 px-4 py-2 rounded-lg font-semibold hover:bg-yellow-600 transition duration-200"
                >
                    + Create Assignment
                </button>
            </div>

            <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-700 text-yellow-400">
                        <tr>
                            <th className="px-6 py-3 text-left text-sm font-bold uppercase tracking-wider">Course</th>
                            <th className="px-6 py-3 text-left text-sm font-bold uppercase tracking-wider">Week</th>
                            <th className="px-6 py-3 text-left text-sm font-bold uppercase tracking-wider">Title</th>
                            <th className="px-6 py-3 text-left text-sm font-bold uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-sm font-bold uppercase tracking-wider">Due Date</th>
                            <th className="px-6 py-3 text-left text-sm font-bold uppercase tracking-wider">Points</th>
                            <th className="px-6 py-3 text-left text-sm font-bold uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-left text-sm font-bold uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-gray-800 divide-y divide-gray-700 text-yellow-300">
                        {assignments.map((assignment) => (
                            <tr
                                key={assignment.id}
                                onClick={() => handleRowClick(assignment.id)}
                                className="hover:bg-gray-700 transition duration-200 cursor-pointer"
                            >
                                <td className="px-6 py-4 text-sm">{assignment.course.name}</td>
                                <td className="px-6 py-4 text-sm">Week {assignment.week.number}</td>
                                <td className="px-6 py-4 text-sm">{assignment.title}</td>
                                <td className="px-6 py-4">
                                    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                                        assignment.type === 'practice' ? 'bg-green-600 text-green-100' : 'bg-blue-600 text-blue-100'
                                    }`}>
                                        {assignment.type === 'practice' ? 'Practice' : 'Graded'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm">{format(new Date(assignment.due_date), 'MMM d, yyyy')}</td>
                                <td className="px-6 py-4 text-sm">{assignment.points_possible} pts</td>
                                <td className="px-6 py-4">
                                    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                                        assignment.is_published ? 'bg-green-600 text-green-100' : 'bg-yellow-600 text-yellow-100'
                                    }`}>
                                        {assignment.is_published ? 'Published' : 'Draft'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm space-x-3 flex">
                                    <button onClick={(e) => handleRowClick(assignment.id)} className="text-yellow-400 hover:text-yellow-300 transition duration-150">
                                        <EyeIcon className="h-5 w-5" />
                                    </button>
                                    <button onClick={(e) => handleEdit(e, assignment.id)} className="text-blue-400 hover:text-blue-300 transition duration-150">
                                        <PencilIcon className="h-5 w-5" />
                                    </button>
                                    <button onClick={(e) => handleDeleteRow(e, assignment.id)} className="text-red-400 hover:text-red-300 transition duration-150">
                                        <TrashIcon className="h-5 w-5" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AssignmentsList;
