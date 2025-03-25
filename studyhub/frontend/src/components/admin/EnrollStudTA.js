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
            if (coursesResponse.success && studentsResponse.success) {
                setCourses(coursesResponse.data || []);
                setStudents(studentsResponse.users || []);
            } else {
                setError('Failed to load courses or students');
            }
        } catch (err) {
            setError('Failed to load courses or students');
        } finally {
            setLoading(false);
        }
    };

    const handleEnroll = async () => {
        try {
            setLoading(true);
            const response = await courseApi.enrollStudent(selectedCourse, selectedStudent, selectedRole);
            if (response.success) {
                navigate('/admin/users');
            } else if (response.status === 409) {
                setError('The selected student/TA is already enrolled in this course.');
            } else {
                setError(response.message || 'Failed to enroll student/TA');
            }
        } catch (err) {
            if (err.status === 409) {
                setError('The selected student/TA is already enrolled in this course.');
            } else {
                setError(err.message || 'Failed to enroll student/TA');
            }
        } finally {
            setLoading(false);
        }
    };

    const filteredStudents = students.filter(student => student.role === selectedRole);

    const FormField = ({ label, value, onChange, options, placeholder }) => (
        <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                {label}
            </label>
            <select className="input-field" value={value} onChange={onChange}>
                <option value="">{placeholder}</option>
                {options.map(option => (
                    <option key={option.id} value={option.id}>
                        {option.name || `${option.first_name} ${option.last_name}`}
                    </option>
                ))}
            </select>
        </div>
    );

    const ErrorDisplay = ({ message }) => (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-4 mb-4">
            {message}
        </div>
    );

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>
        );
    }

    return (
        <div>
            {error && <ErrorDisplay message={error} />}
            <h1 className="text-2xl font-bold text-zinc-900 dark:text-white mb-6">Enroll</h1>
            <div className="glass-card p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                        label="Course"
                        value={selectedCourse}
                        onChange={(e) => setSelectedCourse(e.target.value)}
                        options={courses}
                        placeholder="Select a course"
                    />
                    <FormField
                        label={selectedRole === 'student' ? 'Student' : 'Teaching Assistant'}
                        value={selectedStudent}
                        onChange={(e) => setSelectedStudent(e.target.value)}
                        options={filteredStudents}
                        placeholder={`Select a ${selectedRole === 'student' ? 'student' : 'teaching assistant'}`}
                    />
                    <FormField
                        label="Role"
                        value={selectedRole}
                        onChange={(e) => setSelectedRole(e.target.value)}
                        options={[
                            { id: 'student', name: 'Student' },
                            { id: 'ta', name: 'Teaching Assistant' }
                        ]}
                        placeholder="Select a role"
                    />
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