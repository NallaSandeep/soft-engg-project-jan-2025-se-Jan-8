import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const AssignmentForm = ({ mode = 'create' }) => {
    const navigate = useNavigate();
    const { courseId } = useParams();
    const [assignmentData, setAssignmentData] = useState({
        title: '',
        description: '',
        type: 'practice',
        due_date: '',
        late_submission_penalty: 0,
        is_published: false
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Form submission is disabled.');
    };

    return (
        <div className="p-6 bg-gray-900 min-h-screen text-white">
            <div className="mb-6">
                <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                    <button
                        onClick={() => navigate(courseId ? `/admin/courses/${courseId}/content` : '/admin/assignments')}
                        className="hover:text-yellow-400"
                    >
                        {courseId ? 'Course Content' : 'Assignments'}
                    </button>
                    <span>→</span>
                    <span>{mode === 'edit' ? 'Edit' : 'New'} Assignment</span>
                </div>
                <h1 className="text-2xl font-bold text-yellow-400">
                    {mode === 'edit' ? 'Edit' : 'Add New'} Assignment
                </h1>
            </div>

            <div className="bg-gray-800 rounded-lg shadow p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-yellow-400 mb-1">Title</label>
                        <input
                            type="text"
                            className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:border-yellow-400 focus:ring-yellow-400"
                            value={assignmentData.title}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, title: e.target.value }))}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-yellow-400 mb-1">Description</label>
                        <textarea
                            className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:border-yellow-400 focus:ring-yellow-400"
                            rows="4"
                            value={assignmentData.description}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, description: e.target.value }))}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-yellow-400 mb-1">Type</label>
                        <select
                            className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:border-yellow-400 focus:ring-yellow-400"
                            value={assignmentData.type}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, type: e.target.value }))}
                            required
                        >
                            <option value="practice">Practice</option>
                            <option value="graded">Graded</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-yellow-400 mb-1">Due Date</label>
                        <input
                            type="date"
                            className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:border-yellow-400 focus:ring-yellow-400"
                            value={assignmentData.due_date}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, due_date: e.target.value }))}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-yellow-400 mb-1">Late Submission Penalty (%)</label>
                        <input
                            type="number"
                            min="0"
                            max="100"
                            className="w-full bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:border-yellow-400 focus:ring-yellow-400"
                            value={assignmentData.late_submission_penalty}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, late_submission_penalty: parseFloat(e.target.value) || 0 }))}
                        />
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="is_published"
                            className="h-4 w-4 text-yellow-400 bg-gray-700 border-gray-600 rounded focus:ring-yellow-400"
                            checked={assignmentData.is_published}
                            onChange={(e) => setAssignmentData(prev => ({ ...prev, is_published: e.target.checked }))}
                        />
                        <label htmlFor="is_published" className="ml-2 text-sm text-yellow-400">
                            Published
                        </label>
                    </div>

                    <div className="flex justify-end space-x-3">
                        <button
                            type="button"
                            onClick={() => navigate(courseId ? `/admin/courses/${courseId}/content` : '/admin/assignments')}
                            className="px-4 py-2 text-sm font-medium text-gray-400 hover:text-yellow-400"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="bg-yellow-400 text-gray-900 px-4 py-2 rounded-lg hover:bg-yellow-500"
                        >
                            {mode === 'edit' ? 'Update' : 'Create'} Assignment
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AssignmentForm;
