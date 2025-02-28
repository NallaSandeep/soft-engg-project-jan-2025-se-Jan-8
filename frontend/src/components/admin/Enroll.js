import React, { useState, useEffect } from 'react';
import { courseApi, userApi } from '../../services/apiService';

const Enroll = () => {
    const [courses, setCourses] = useState([]);
    const [users, setUsers] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState('');
    const [selectedUser, setSelectedUser] = useState('');
    const [role, setRole] = useState('student');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCoursesAndUsers();
    }, []);

    const fetchCoursesAndUsers = async () => {
        try {
            setLoading(true);
            const [coursesResponse, usersResponse] = await Promise.all([
                courseApi.getCourses(),
                userApi.getUsers()
            ]);
            setCourses(coursesResponse.data || []);
            setUsers(usersResponse.users || []); // Ensure usersResponse.users is used
        } catch (err) {
            setError('Failed to load data');
            console.error('Error loading data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleEnroll = async () => {
        try {
            if (role === 'student') {
                await courseApi.enrollStudent(selectedCourse, selectedUser);
            } else {
                await courseApi.enrollTA(selectedCourse, selectedUser);
            }
            alert('User enrolled successfully');
        } catch (err) {
            setError('Failed to enroll user');
            console.error('Error enrolling user:', err);
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold mb-8">Enroll Students/TAs to Course</h1>
            {error && <div className="text-red-500 mb-4">{error}</div>}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Select Course</label>
                <select
                    value={selectedCourse}
                    onChange={(e) => setSelectedCourse(e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                >
                    <option value="">Select a course</option>
                    {courses.map(course => (
                        <option key={course.id} value={course.id}>{course.name}</option>
                    ))}
                </select>
            </div>
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Select User</label>
                <select
                    value={selectedUser}
                    onChange={(e) => setSelectedUser(e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                >
                    <option value="">Select a user</option>
                    {users.map(user => (
                        <option key={user.id} value={user.id}>{user.first_name} {user.last_name}</option>
                    ))}
                </select>
            </div>
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Role</label>
                <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
                >
                    <option value="student">Student</option>
                    <option value="ta">Teaching Assistant</option>
                </select>
            </div>
            <button
                onClick={handleEnroll}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
                Enroll
            </button>
        </div>
    );
};

export default Enroll;
