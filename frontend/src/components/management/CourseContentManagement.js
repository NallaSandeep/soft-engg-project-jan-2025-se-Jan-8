import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { courseApi } from '../../services/apiService';
import AssignmentManagement from './AssignmentManagement';
import ConfirmDialog from '../common/ConfirmDialog';

const CourseContentManagement = () => {
    const { courseId } = useParams();
    const [course, setCourse] = useState(null);
    const [weeks, setWeeks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddWeekForm, setShowAddWeekForm] = useState(false);
    const [showAddLectureForm, setShowAddLectureForm] = useState(null); // weekId or null
    const [weekFormData, setWeekFormData] = useState({
        number: '',
        title: '',
        description: '',
        is_published: false
    });
    const [lectureFormData, setLectureFormData] = useState({
        title: '',
        description: '',
        youtube_url: '',
        is_published: false
    });
    const [editingLecture, setEditingLecture] = useState(null);
    const [deleteConfirm, setDeleteConfirm] = useState({
        show: false,
        type: null, // 'lecture' or 'assignment'
        itemId: null,
        weekId: null
    });

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            const response = await courseApi.getCourseContent(courseId);
            setCourse(response.data.data.course);
            setWeeks(response.data.data.course.weeks || []);
        } catch (err) {
            setError('Failed to load course content');
        } finally {
            setLoading(false);
        }
    };

    const handleWeekSubmit = async (e) => {
        e.preventDefault();
        try {
            await courseApi.createWeek(courseId, weekFormData);
            setShowAddWeekForm(false);
            setWeekFormData({
                number: '',
                title: '',
                description: '',
                is_published: false
            });
            fetchCourseContent();
        } catch (err) {
            setError('Failed to create week');
        }
    };

    const handleLectureSubmit = async (e, weekId) => {
        e.preventDefault();
        try {
            await courseApi.createLecture(weekId, lectureFormData);
            setShowAddLectureForm(null);
            setLectureFormData({
                title: '',
                description: '',
                youtube_url: '',
                is_published: false
            });
            fetchCourseContent();
        } catch (err) {
            setError('Failed to create lecture');
        }
    };

    const handleEditLecture = (lecture) => {
        setEditingLecture(lecture);
        setLectureFormData({
            title: lecture.title,
            description: lecture.description || '',
            youtube_url: lecture.youtube_url,
            is_published: lecture.is_published
        });
        setShowAddLectureForm(lecture.week_id);
    };

    const handleUpdateLecture = async (e, weekId) => {
        e.preventDefault();
        try {
            await courseApi.updateLecture(editingLecture.id, lectureFormData);
            setShowAddLectureForm(null);
            setEditingLecture(null);
            setLectureFormData({
                title: '',
                description: '',
                youtube_url: '',
                is_published: false
            });
            fetchCourseContent();
        } catch (err) {
            setError('Failed to update lecture');
        }
    };

    const handleDeleteLecture = async (lectureId, weekId) => {
        try {
            await courseApi.deleteLecture(lectureId);
            fetchCourseContent();
        } catch (err) {
            setError('Failed to delete lecture');
        }
    };

    const handleDeleteAssignment = async (assignmentId, weekId) => {
        try {
            await courseApi.deleteAssignment(assignmentId);
            fetchCourseContent();
        } catch (err) {
            setError('Failed to delete assignment');
        }
    };

    const confirmDelete = (type, itemId, weekId) => {
        setDeleteConfirm({
            show: true,
            type,
            itemId,
            weekId
        });
    };

    const handleConfirmDelete = () => {
        const { type, itemId, weekId } = deleteConfirm;
        if (type === 'lecture') {
            handleDeleteLecture(itemId, weekId);
        } else if (type === 'assignment') {
            handleDeleteAssignment(itemId, weekId);
        }
        setDeleteConfirm({ show: false, type: null, itemId: null, weekId: null });
    };

    if (loading) return <div>Loading course content...</div>;
    if (error) return <div className="text-red-500">{error}</div>;
    if (!course) return <div>Course not found</div>;

    return (
        <div className="container mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-bold mb-2">{course.name}</h1>
                <p className="text-gray-600">{course.code}</p>
            </div>

            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Course Content</h2>
                <button
                    onClick={() => setShowAddWeekForm(true)}
                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                >
                    Add New Week
                </button>
            </div>

            {/* Add Week Form */}
            {showAddWeekForm && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h3 className="text-lg font-semibold mb-4">Add New Week</h3>
                    <form onSubmit={handleWeekSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Week Number</label>
                            <input
                                type="number"
                                value={weekFormData.number}
                                onChange={(e) => setWeekFormData(prev => ({ ...prev, number: e.target.value }))}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Title</label>
                            <input
                                type="text"
                                value={weekFormData.title}
                                onChange={(e) => setWeekFormData(prev => ({ ...prev, title: e.target.value }))}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Description</label>
                            <textarea
                                value={weekFormData.description}
                                onChange={(e) => setWeekFormData(prev => ({ ...prev, description: e.target.value }))}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                rows="3"
                            />
                        </div>
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                checked={weekFormData.is_published}
                                onChange={(e) => setWeekFormData(prev => ({ ...prev, is_published: e.target.checked }))}
                                className="h-4 w-4 text-blue-600 rounded"
                            />
                            <label className="ml-2 text-sm text-gray-700">Publish Week</label>
                        </div>
                        <div className="flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={() => setShowAddWeekForm(false)}
                                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                            >
                                Create Week
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Weeks List */}
            <div className="space-y-6">
                {weeks.map(week => (
                    <div key={week.id} className="bg-white rounded-lg shadow p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold">
                                Week {week.number}: {week.title}
                            </h3>
                            <div className="space-x-2">
                                <button
                                    onClick={() => setShowAddLectureForm(week.id)}
                                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                >
                                    Add Lecture
                                </button>
                                <AssignmentManagement
                                    weekId={week.id}
                                    onAssignmentAdded={fetchCourseContent}
                                />
                            </div>
                        </div>

                        {/* Add Lecture Form */}
                        {showAddLectureForm === week.id && (
                            <div className="bg-gray-50 rounded p-4 mb-4">
                                <h4 className="text-md font-semibold mb-3">Add New Lecture</h4>
                                <form onSubmit={(e) => handleLectureSubmit(e, week.id)} className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Title</label>
                                        <input
                                            type="text"
                                            value={lectureFormData.title}
                                            onChange={(e) => setLectureFormData(prev => ({ ...prev, title: e.target.value }))}
                                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">YouTube URL</label>
                                        <input
                                            type="url"
                                            value={lectureFormData.youtube_url}
                                            onChange={(e) => setLectureFormData(prev => ({ ...prev, youtube_url: e.target.value }))}
                                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Description</label>
                                        <textarea
                                            value={lectureFormData.description}
                                            onChange={(e) => setLectureFormData(prev => ({ ...prev, description: e.target.value }))}
                                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                                            rows="3"
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <input
                                            type="checkbox"
                                            checked={lectureFormData.is_published}
                                            onChange={(e) => setLectureFormData(prev => ({ ...prev, is_published: e.target.checked }))}
                                            className="h-4 w-4 text-blue-600 rounded"
                                        />
                                        <label className="ml-2 text-sm text-gray-700">Publish Lecture</label>
                                    </div>
                                    <div className="flex justify-end space-x-3">
                                        <button
                                            type="button"
                                            onClick={() => setShowAddLectureForm(null)}
                                            className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            type="submit"
                                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                                        >
                                            Add Lecture
                                        </button>
                                    </div>
                                </form>
                            </div>
                        )}

                        {/* Lectures List */}
                        <div className="space-y-3">
                            {week.lectures?.map(lecture => (
                                <div
                                    key={lecture.id}
                                    className="flex items-center justify-between p-3 bg-gray-50 rounded"
                                >
                                    <div>
                                        <h4 className="font-medium">{lecture.title}</h4>
                                        <p className="text-sm text-gray-600">
                                            {lecture.is_published ? 'Published' : 'Draft'}
                                        </p>
                                    </div>
                                    <div className="space-x-2">
                                        <button
                                            onClick={() => handleEditLecture(lecture)}
                                            className="text-blue-500 hover:text-blue-600"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => confirmDelete('lecture', lecture.id, week.id)}
                                            className="text-red-500 hover:text-red-600"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Assignments List */}
                        <div className="mt-6">
                            <h4 className="text-md font-semibold mb-3">Assignments</h4>
                            <div className="space-y-3">
                                {week.assignments?.map(assignment => (
                                    <div
                                        key={assignment.id}
                                        className="flex items-center justify-between p-3 bg-gray-50 rounded"
                                    >
                                        <div>
                                            <h5 className="font-medium">{assignment.title}</h5>
                                            <div className="text-sm text-gray-600">
                                                <span className="mr-3">Type: {assignment.type}</span>
                                                {assignment.due_date && (
                                                    <span>Due: {new Date(assignment.due_date).toLocaleString()}</span>
                                                )}
                                            </div>
                                        </div>
                                        <div className="space-x-2">
                                            <button
                                                onClick={() => confirmDelete('assignment', assignment.id, week.id)}
                                                className="text-red-500 hover:text-red-600"
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Confirmation Dialog */}
            <ConfirmDialog
                isOpen={deleteConfirm.show}
                title="Confirm Delete"
                message={`Are you sure you want to delete this ${deleteConfirm.type}? This action cannot be undone.`}
                onConfirm={handleConfirmDelete}
                onCancel={() => setDeleteConfirm({ show: false, type: null, itemId: null, weekId: null })}
            />
        </div>
    );
};

export default CourseContentManagement; 