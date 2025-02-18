import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';
import 'bootstrap/dist/css/bootstrap.min.css';

const CourseContent = () => {
    const navigate = useNavigate();
    const { courseId } = useParams();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const mockCourses = {
        1: {
            name: 'Introduction to Programming',
            code: 'CS101',
            description: 'An introductory course covering programming basics using Python.',
            is_active: true,
            enrolled_count: 5,
            max_students: 30,
            teaching_assistants: 2,
            created_by: 'Prof. John Doe',
            start_date: '2024-03-01',
            end_date: '2024-06-30',
            weeks: [
                {
                    id: 101,
                    number: 1,
                    title: 'Getting Started with Python',
                    description: 'Introduction to Python syntax, variables, and data types.',
                    lectures: [
                        { id: 201, title: 'Introduction to Python', description: 'Understanding basic Python syntax.' }
                    ],
                    assignments: [
                        { id: 301, title: 'Practice Assigment 1.1', due_date: '2025-12-31' },
                        { id: 302, title: 'Graded Assignment 1', due_date: '2025-02-26' },
                        { id: 303, title: 'Practice Assigment 2.1', due_date: '2025-12-31' }
                    ]
                }
            ]
        },
        2: {
            name: 'Data Structures',
            code: 'CS102',
            description: 'A deep dive into fundamental data structures like arrays, linked lists, trees, and graphs.',
            is_active: true,
            enrolled_count: 8,
            max_students: 40,
            teaching_assistants: 3,
            created_by: 'Dr. Alice Smith',
            start_date: '2024-08-15',
            end_date: '2024-12-10',
            weeks: [
                {
                    id: 102,
                    number: 1,
                    title: 'Introduction to Data Structures',
                    description: 'Overview of different types of data structures and their use cases.',
                    lectures: [
                        { id: 202, title: 'Arrays and Linked Lists', description: 'Understanding how arrays and linked lists work.' }
                    ],
                    assignments: []
                },
                {
                    id: 103,
                    number: 2,
                    title: 'Stacks and Queues',
                    description: 'Exploring stack and queue data structures with real-world applications.',
                    lectures: [
                        { id: 203, title: 'Stack Implementation', description: 'LIFO concept and stack operations.' }
                    ],
                    assignments: []
                }
            ]
        },
        3: {
            name: 'Introduction to Machine Learning',
            code: 'ML101',
            description: 'A beginner-friendly course on the fundamentals of Machine Learning, including supervised and unsupervised learning techniques.',
            is_active: true,
            enrolled_count: 10,
            max_students: 35,
            teaching_assistants: 4,
            created_by: 'Dr. Robert Lee',
            start_date: '2025-01-15',
            end_date: '2025-05-05',
            weeks: [
                {
                    id: 104,
                    number: 1,
                    title: 'Introduction to Machine Learning',
                    description: 'Understanding the basics of ML, types of learning, and real-world applications.',
                    lectures: [
                        { id: 204, title: 'Supervised vs Unsupervised Learning', description: 'Key differences and practical examples.' }
                    ],
                    assignments: [
                        { id: 304, title: 'Predictive Modeling Exercise', due_date: '2025-01-25' }
                    ]
                },
                {
                    id: 105,
                    number: 2,
                    title: 'Regression and Classification',
                    description: 'Deep dive into regression and classification techniques with hands-on exercises.',
                    lectures: [
                        { id: 205, title: 'Linear Regression', description: 'Understanding linear regression and its applications.' }
                    ],
                    assignments: []
                }
            ]
        }
    };
    
    useEffect(() => {
        setLoading(true);
        setTimeout(() => {
            if (mockCourses[courseId]) {
                setCourse(mockCourses[courseId]);
            } else {
                setError('Course not found');
            }
            setLoading(false);
        }, 1000);
    }, [courseId]);

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100 text-warning fw-bold fs-4">
                Loading course content...
            </div>
        );
    }

    if (error) {
        return (
            <div className="container p-4">
                <div className="alert alert-danger">{error}</div>
            </div>
        );
    }

    return (
        <div className="container-fluid p-4 text-white" style={{ backgroundColor: '#121212', minHeight: '100vh' }}>
            {/* Breadcrumbs */}
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <button className="btn btn-outline-warning btn-sm" onClick={() => navigate('/admin/courses')}>
                        ← Back to Courses
                    </button>
                    <h1 className="mt-3 text-warning fw-bold">{course.name}</h1>
                    <p className="text-muted">{course.code}</p>
                </div>
                <div>
                    <button className="btn btn-outline-info me-2" onClick={() => navigate(`/admin/courses/${courseId}/edit`)}>
                        <FaEdit /> Edit Course
                    </button>
                    <button className="btn btn-outline-danger" onClick={() => alert('Course deleted')}>
                        <FaTrash /> Delete Course
                    </button>
                </div>
            </div>

            {/* Course Details */}
            <div className="card bg-dark text-white mb-4 shadow-sm border border-warning">
                <div className="card-body">
                    <h5 className="card-title text-warning">Course Details</h5>
                    <p className="card-text">{course.description}</p>
                    <p>
                        <strong>Status:</strong> <span className={course.is_active ? 'text-success' : 'text-danger'}>
                            {course.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </p>
                    <p><strong>Enrollment:</strong> {course.enrolled_count}/{course.max_students}</p>
                    <p><strong>Created By:</strong> {course.created_by}</p>
                    <p><strong>Duration:</strong> {new Date(course.start_date).toLocaleDateString()} - {new Date(course.end_date).toLocaleDateString()}</p>
                </div>
            </div>

            {/* Weeks Section */}
            {course.weeks.map(week => (
                <div key={week.id} className="card bg-dark text-white mb-3 shadow-sm border border-secondary">
                    <div className="card-header d-flex justify-content-between align-items-center bg-secondary">
                        <h5 className="mb-0">Week {week.number}: {week.title}</h5>
                        <button className="btn btn-sm btn-outline-info" onClick={() => navigate(`/admin/courses/${courseId}/weeks/${week.id}/edit`)}>
                            <FaEdit /> Edit Week
                        </button>
                    </div>
                    <div className="card-body">
                        <p>{week.description}</p>

                        {/* Lectures */}
                        <h6 className="text-warning">Lectures</h6>
                        <ul className="list-group mb-3">
                            {week.lectures.length > 0 ? week.lectures.map(lecture => (
                                <li key={lecture.id} className="list-group-item bg-secondary text-white d-flex justify-content-between align-items-center">
                                    <span>{lecture.title} - {lecture.description}</span>
                                    <button className="btn btn-sm btn-outline-danger">
                                        <FaTrash />
                                    </button>
                                </li>
                            )) : <li className="list-group-item bg-secondary text-white">No lectures added yet</li>}
                        </ul>

                        {/* Add Lecture Button */}
                        <button 
                            className="btn btn-outline-warning btn-sm mb-3" 
                            onClick={() => navigate(`/admin/courses/${courseId}/weeks/${week.id}/lectures/new`)}
                        >
                            <FaPlus /> Add Lecture
                        </button>

                        {/* Assignments */}
                        <h6 className="text-warning">Assignments</h6>
                        <ul className="list-group">
                            {week.assignments.length > 0 ? week.assignments.map(assignment => (
                                <li key={assignment.id} className="list-group-item bg-secondary text-white d-flex justify-content-between align-items-center">
                                    <span>{assignment.title} (Due: {new Date(assignment.due_date).toLocaleDateString()})</span>
                                    <button className="btn btn-sm btn-outline-danger">
                                        <FaTrash />
                                    </button>
                                </li>
                            )) : <li className="list-group-item bg-secondary text-white">No assignments added yet</li>}
                        </ul>

                        {/* Add Assignment Button */}
                        <button 
                            className="btn btn-outline-warning btn-sm mt-3" 
                            onClick={() => navigate(`/admin/courses/${courseId}/weeks/${week.id}/assignments/new`)}
                        >
                            <FaPlus /> Add Assignment
                        </button>
                    </div>
                </div>
            ))}

            {/* Add Week Button */}
            <button className="btn btn-outline-warning w-100 mt-3 fw-bold" onClick={() => navigate(`/admin/courses/${courseId}/weeks/new`)}>
                <FaPlus /> Add New Week
            </button>
        </div>
    );
};

export default CourseContent;


