import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaEdit } from 'react-icons/fa';
import 'bootstrap/dist/css/bootstrap.min.css';

const CoursesList = () => {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Mock placeholder courses
    const mockCourses = [
        { id: 1, name: 'Introduction to Programming', code: 'CS101', enrolled_count: 5, max_students: 30, is_active: true },
        { id: 2, name: 'Data Structures', code: 'CS102', enrolled_count: 5, max_students: 25, is_active: true },
        { id: 3, name: 'Introduction to ML', code: 'ML101', enrolled_count: 5, max_students: 50, is_active: true }
    ];

    useEffect(() => {
        setLoading(true);
        setTimeout(() => {
            setCourses(mockCourses);
            setLoading(false);
        }, 1000); // Simulate API call
    }, []);

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100 text-warning fs-4">
                Loading courses...
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4">
                <div className="alert alert-danger">{error}</div>
            </div>
        );
    }

    return (
        <div className="container-fluid p-4 text-white" style={{ backgroundColor: '#121212', minHeight: '100vh' }}>
            {/* Header & Create Button */}
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1 className="text-warning fw-bold">Courses</h1>
                <button className="btn btn-warning fw-bold px-4 py-2 shadow-sm" onClick={() => navigate('/admin/courses/new')}>
                    + Create Course
                </button>
            </div>

            {/* Course Table */}
            <div className="table-responsive">
                <table className="table table-dark table-hover align-middle text-center">
                    <thead>
                        <tr className="text-warning">
                            <th className="py-3">Course</th>
                            <th className="py-3">Code</th>
                            <th className="py-3">Students</th>
                            <th className="py-3">Status</th>
                            <th className="py-3">Edit</th>
                        </tr>
                    </thead>
                    <tbody>
                        {courses.map(course => (
                            <tr 
                                key={course.id} 
                                className="cursor-pointer"
                                onClick={() => navigate(`/admin/courses/${course.id}/content`)}
                                style={{ transition: '0.3s', cursor: 'pointer' }}
                                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1e1e1e'}
                                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = ''} 
                            >
                                <td className="py-3">{course.name}</td>
                                <td className="py-3">{course.code}</td>
                                <td className="py-3">
                                    {course.enrolled_count} {course.max_students ? `/ ${course.max_students}` : '(Unlimited)'}
                                </td>
                                <td className="py-3">
                                    <span className={`badge px-3 py-2 fs-6 ${course.is_active ? 'bg-success' : 'bg-danger'}`}>
                                        {course.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                <td className="py-3">
                                    <button
                                        className="btn btn-sm btn-outline-warning rounded-circle d-flex align-items-center justify-content-center"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            navigate(`/admin/courses/${course.id}/edit`);
                                        }}
                                        title="Edit"
                                        style={{ width: '36px', height: '36px' }}
                                    >
                                        <FaEdit />
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

export default CoursesList;
