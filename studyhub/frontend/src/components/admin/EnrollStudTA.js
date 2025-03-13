import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { courseApi, userApi } from '../../services/apiService';

const EnrollStudents = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [students, setStudents] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState('');
    const [selectedStudent, setSelectedStudent] = useState('');
    const [selectedRole, setSelectedRole] = useState('student');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCoursesAndStudents();
    }, []);

    useEffect(() => {
        setSelectedStudent(''); // Reset selected student when role changes
    }, [selectedRole]);

    const fetchCoursesAndStudents = async () => {
        try {
            setLoading(true);
            const [coursesResponse, studentsResponse] = await Promise.all([
                courseApi.getCourses(),
                userApi.getUsers()
            ]);
            console.log(coursesResponse, studentsResponse);
            if (coursesResponse.success && studentsResponse.success) {
                setCourses(coursesResponse.data || []);
                setStudents(studentsResponse.users || []);
            } else {
                setError('Failed to load courses or students');
            }
        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Failed to load courses or students');
        } finally {
            setLoading(false);
        }
    };

    const handleEnroll = async () => {
        try {
            setLoading(true);
            const response = await courseApi.enrollStudent(selectedCourse, selectedStudent, selectedRole);
            console.log('Enroll response:', response);
            if (response.success) {
                navigate('/admin/users');
            } else {
                setError(response.message || 'Failed to enroll student');
            }
        } catch (err) {
            console.error('Error enrolling student:', err);
            setError('Failed to enroll student');
        } finally {
            setLoading(false);
        }
    };

    const filteredStudents = students.filter(student => student.role === selectedRole);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div>
            <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-6">Enroll Students</h1>
            <div className="glass-card p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Course
                        </label>
                        <select
                            className="input-field"
                            value={selectedCourse}
                            onChange={(e) => setSelectedCourse(e.target.value)}
                        >
                            <option value="">Select a course</option>
                            {courses.map(course => (
                                <option key={course.id} value={course.id}>
                                    {course.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            {selectedRole === 'student' ? 'Student' : 'Teaching Assistant'}
                        </label>
                        <select
                            className="input-field"
                            value={selectedStudent}
                            onChange={(e) => setSelectedStudent(e.target.value)}
                        >
                            <option value="">Select a {selectedRole === 'student' ? 'student' : 'teaching assistant'}</option>
                            {filteredStudents.map(student => (
                                <option key={student.id} value={student.id}>
                                    {student.first_name} {student.last_name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                            Role
                        </label>
                        <select
                            className="input-field"
                            value={selectedRole}
                            onChange={(e) => setSelectedRole(e.target.value)}
                        >
                            <option value="student">Student</option>
                            <option value="ta">Teaching Assistant</option>
                        </select>
                    </div>
                </div>
                <div className="mt-6">
                    <button
                        onClick={handleEnroll}
                        className="btn-primary"
                        disabled={!selectedCourse || !selectedStudent}
                    >
                        Enroll
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EnrollStudents;