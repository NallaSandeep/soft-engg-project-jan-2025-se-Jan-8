import React, { useState } from 'react';
import { assignmentApi } from '../../services/apiService';

const AssignmentManagement = ({ weekId, onAssignmentAdded }) => {
    const [showForm, setShowForm] = useState(false);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        type: 'practice',
        due_date: '',
        is_published: false
    });

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await assignmentApi.createAssignment(weekId, formData);
            setShowForm(false);
            setFormData({
                title: '',
                description: '',
                type: 'practice',
                due_date: '',
                is_published: false
            });
            if (onAssignmentAdded) {
                onAssignmentAdded();
            }
        } catch (err) {
            setError('Failed to create assignment');
        }
    };

    return (
        <div>
            <button
                onClick={() => setShowForm(true)}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
                Add Assignment
            </button>

            {showForm && (
                <div className="mt-4 bg-gray-50 rounded p-4">
                    <h4 className="text-lg font-semibold mb-4">Add New Assignment</h4>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Title</label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Description</label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                rows="3"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Type</label>
                            <select
                                name="type"
                                value={formData.type}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                            >
                                <option value="practice">Practice</option>
                                <option value="graded">Graded</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Due Date</label>
                            <input
                                type="datetime-local"
                                name="due_date"
                                value={formData.due_date}
                                onChange={handleInputChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                            />
                        </div>
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                name="is_published"
                                checked={formData.is_published}
                                onChange={handleInputChange}
                                className="h-4 w-4 text-blue-600 rounded"
                            />
                            <label className="ml-2 text-sm text-gray-700">Publish Assignment</label>
                        </div>

                        {error && <div className="text-red-500 text-sm">{error}</div>}

                        <div className="flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={() => setShowForm(false)}
                                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                            >
                                Create Assignment
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </div>
    );
};

export default AssignmentManagement; 