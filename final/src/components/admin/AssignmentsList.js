import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { 
    PencilIcon, 
    TrashIcon, 
    EyeIcon,
    PlusIcon,
    ClipboardDocumentListIcon
} from '@heroicons/react/24/outline';


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
        <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900">
            <div className="max-w-7xl mx-auto space-y-8 p-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
                            Assignments
                        </h1>
                        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                            Manage course assignments
                        </p>
                    </div>
                    <button
                        onClick={() => navigate('/admin/assignments/new')}
                        className="flex items-center space-x-2 px-4 py-2 rounded-lg
                                 bg-zinc-800 dark:bg-white
                                 text-white dark:text-zinc-900
                                 hover:bg-zinc-700 dark:hover:bg-zinc-100
                                 transition-colors duration-200"
                    >
                        <PlusIcon className="h-5 w-5" />
                        <span>Create Assignment</span>
                    </button>
                </div>

                {/* Assignments Table */}
                <div className="bg-white/60 dark:bg-zinc-800/40 backdrop-blur-sm rounded-xl 
                              shadow-[0_2px_8px_-3px_rgba(0,0,0,0.05)] 
                              dark:shadow-[0_2px_8px_-3px_rgba(0,0,0,0.2)]">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-zinc-200 dark:border-zinc-700">
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Course</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Week</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Title</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Type</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Due Date</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Points</th>
                                    <th className="text-left p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Status</th>
                                    <th className="text-right p-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {assignments.map((assignment) => (
                                    <tr
                                        key={assignment.id}
                                        onClick={() => handleRowClick(assignment.id)}
                                        className="border-b border-zinc-200 dark:border-zinc-700 last:border-0
                                                 hover:bg-zinc-50 dark:hover:bg-zinc-800/50
                                                 transition-colors duration-200 cursor-pointer"
                                    >
                                        <td className="p-4">
                                            <div className="flex items-center space-x-3">
                                                <ClipboardDocumentListIcon className="h-5 w-5 text-zinc-400 dark:text-zinc-500" />
                                                <span className="font-medium text-zinc-900 dark:text-white">
                                                    {assignment.course.code}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="p-4 text-zinc-600 dark:text-zinc-400">
                                            Week {assignment.week.number}
                                        </td>
                                        <td className="p-4 text-zinc-600 dark:text-zinc-400">
                                            {assignment.title}
                                        </td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                                ${assignment.type === 'practice'
                                                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-800 dark:text-emerald-100'
                                                    : 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                                                }`}
                                            >
                                                {assignment.type.charAt(0).toUpperCase() + assignment.type.slice(1)}
                                            </span>
                                        </td>
                                        <td className="p-4 text-zinc-600 dark:text-zinc-400">
                                            {format(new Date(assignment.due_date), 'MMM d, yyyy')}
                                        </td>
                                        <td className="p-4 text-zinc-600 dark:text-zinc-400">
                                            {assignment.points_possible} pts
                                        </td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                                ${assignment.is_published
                                                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-800 dark:text-emerald-100'
                                                    : 'bg-amber-100 text-amber-800 dark:bg-amber-800 dark:text-amber-100'
                                                }`}
                                            >
                                                {assignment.is_published ? 'Published' : 'Draft'}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex justify-end space-x-2">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleRowClick(assignment.id);
                                                    }}
                                                    className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-700
                                                             text-zinc-600 dark:text-zinc-400
                                                             transition-colors duration-200"
                                                >
                                                    <EyeIcon className="h-5 w-5" />
                                                </button>
                                                <button
                                                    onClick={(e) => handleEdit(e, assignment.id)}
                                                    className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-700
                                                             text-zinc-600 dark:text-zinc-400
                                                             transition-colors duration-200"
                                                >
                                                    <PencilIcon className="h-5 w-5" />
                                                </button>
                                                <button
                                                    onClick={(e) => handleDeleteRow(e, assignment.id)}
                                                    className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20
                                                             text-red-600 dark:text-red-400
                                                             transition-colors duration-200"
                                                >
                                                    <TrashIcon className="h-5 w-5" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssignmentsList;