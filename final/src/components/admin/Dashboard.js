import React from 'react';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

const AdminDashboard = () => {
    const navigate = useNavigate();
    
    const stats = {
        totalCourses: 4,
        totalStudents: 5,
        totalAssignments: 10,
        totalQuestions: 50,
        recentCourses: [
            { id: 1, name: 'Introduction to Programming', code: 'CS101', created_at: '2025-02-01' },
            { id: 2, name: 'Data Structures', code: 'CS102', created_at: '2025-01-20' },
            { id: 3, name: 'Introduction to ML', code: 'ML101', created_at: '2025-01-20' }
        ],
        recentAssignments: [
            { id: 1, title: 'Practice Assignment 1.1', due_date: '2025-02-10', is_published: true },
            { id: 2, title: 'Graded Assignment 1', due_date: '2025-02-15', is_published: false },
            { id: 3, title: 'Practice Assignment 2.1', due_date: '2025-02-10', is_published: true }
        ]
    };
    
    return (
        <div className="container-fluid py-5 text-white" style={{ backgroundColor: '#121212', minHeight: '100vh' }}>
            <h1 className="text-warning mb-4 fw-bold border-bottom pb-2">Admin Dashboard</h1>

            {/* Stats Grid */}
            <div className="row g-4">
                {[
                    { title: 'Total Courses', value: stats.totalCourses, route: '/admin/courses' },
                    { title: 'Total Students', value: stats.totalStudents, route: '/admin/users' },
                    { title: 'Total Assignments', value: stats.totalAssignments, route: '/admin/assignments' },
                    { title: 'Question Bank', value: stats.totalQuestions, route: '/admin/question-bank' }
                ].map((item, index) => (
                    <div key={index} className="col-md-3">
                        <div 
                            className="card bg-dark text-warning p-4 shadow-lg rounded border border-warning"
                            onClick={() => navigate(item.route)}
                            style={{ cursor: 'pointer', transition: '0.3s' }}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                        >
                            <h5 className="fw-bold">{item.title}</h5>
                            <h2 className="display-5 fw-bold">{item.value}</h2>
                        </div>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="mt-5">
                <h2 className="text-warning fw-bold mb-3">Quick Actions</h2>
                <div className="d-flex flex-wrap gap-3">
                    {[
                        { text: 'Create Course', route: '/admin/courses/new' },
                        { text: 'Create Assignment', route: '/admin/assignments/new' },
                        { text: 'Add Question', route: '/admin/question-bank/new' },
                        { text: 'Add User', route: '/admin/users/new' }
                    ].map((action, index) => (
                        <button 
                            key={index}
                            className="btn btn-warning fw-bold px-4 py-2 rounded-pill shadow-sm"
                            onClick={() => navigate(action.route)}
                        >
                            {action.text}
                        </button>
                    ))}
                </div>
            </div>

            {/* Recent Activity */}
            <div className="mt-5 row">
                {/* Recent Courses */}
                <div className="col-md-6">
                    <h3 className="text-warning fw-bold border-bottom pb-2">Recent Courses</h3>
                    <ul className="list-group mt-3">
                        {stats.recentCourses.map(course => (
                            <li 
                                key={course.id} 
                                className="list-group-item bg-dark text-white border-warning d-flex justify-content-between align-items-center shadow-sm rounded"
                                onClick={() => navigate(`/admin/courses/${course.id}/content`)}
                                style={{ cursor: 'pointer', transition: '0.3s', padding: '12px' }}
                                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#222'}
                                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'black'}
                            >
                                <span className="fw-bold">{course.name} <small className="text-muted">({course.code})</small></span>
                                <small className="text-warning">{new Date(course.created_at).toLocaleDateString()}</small>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Recent Assignments */}
                <div className="col-md-6">
                    <h3 className="text-warning fw-bold border-bottom pb-2">Recent Assignments</h3>
                    <ul className="list-group mt-3">
                        {stats.recentAssignments.map(assignment => (
                            <li 
                                key={assignment.id} 
                                className="list-group-item bg-dark text-white border-warning d-flex justify-content-between align-items-center shadow-sm rounded"
                                onClick={() => navigate(`/admin/assignments/${assignment.id}`)}
                                style={{ cursor: 'pointer', transition: '0.3s', padding: '12px' }}
                                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#222'}
                                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'black'}
                            >
                                <span className="fw-bold">{assignment.title} <small className="text-muted">- Due: {new Date(assignment.due_date).toLocaleDateString()}</small></span>
                                <span className={`badge px-3 py-2 fw-bold ${assignment.is_published ? 'bg-success' : 'bg-warning'}`}>
                                    {assignment.is_published ? 'Published' : 'Draft'}
                                </span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
