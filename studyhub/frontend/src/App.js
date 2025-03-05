import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { ThemeProvider } from './contexts/ThemeContext';
import { ModalProvider, ModalContainer } from './components/common/Modal';
import { DropdownProvider } from './components/common/Dropdown';
import PrivateRoute from './components/auth/PrivateRoute';
import Layout from './components/layout/Layout';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ForgotPassword from './components/auth/ForgotPassword';
import ResetPassword from './components/auth/ResetPassword';

// Common Components
import Dashboard from './components/Dashboard';

// Student Components
import StudentDashboard from './components/student/Dashboard';
import StudentCourses from './components/student/MyCourses';
import AssignmentList from './components/assignments/AssignmentList';
import CourseView from './components/student/CourseView';
import LectureView from './components/student/LectureView';
import AssignmentView from './components/assignments/AssignmentView';
import KnowledgeBase from './components/personal/KnowledgeBase';
import KnowledgeBaseLanding from './components/personal/KnowledgeBaseLanding';

// Admin Routes
import adminRoutes from './routes/AdminRoutes';

// TA Components
import TADashboard from './components/ta/Dashboard';
import TAAssignments from './components/ta/AssignmentGrading';
import TACourses from './components/ta/Courses';

// TA Routes
const taRoutes = [
    {
        path: '/ta',
        children: [
            { path: 'dashboard', element: <TADashboard /> },
            { path: 'assignments', element: <TAAssignments /> },
            { path: 'courses', element: <TACourses /> },
        ]
    }
];

const App = () => {
    const renderRoutes = (routes) => {
        return routes.map((route, index) => {
            if (route.children) {
                return (
                    <Route key={index} path={route.path} element={route.element}>
                        {renderRoutes(route.children)}
                    </Route>
                );
            }
            return <Route key={index} path={route.path} element={route.element} />;
        });
    };

    return (
        <Router>
            <ThemeProvider>
                <AuthProvider>
                    <ModalProvider>
                        <DropdownProvider>
                            <Routes>
                                {/* Public Routes */}
                                <Route path="/login" element={<Login />} />
                                <Route path="/register" element={<Register />} />
                                <Route path="/forgot-password" element={<ForgotPassword />} />
                                <Route path="/reset-password/:token" element={<ResetPassword />} />

                                {/* Protected Routes */}
                                <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
                                    {/* Default redirect */}
                                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                                    
                                    {/* Common Dashboard */}
                                    <Route path="/dashboard" element={<Dashboard />} />

                                    {/* Student Routes */}
                                    <Route path="/student">
                                        <Route path="dashboard" element={<StudentDashboard />} />
                                        <Route path="courses" element={<StudentCourses />} />
                                        <Route path="assignments" element={<AssignmentList />} />
                                    </Route>

                                    {/* TA Routes */}
                                    {renderRoutes(taRoutes)}

                                    {/* Course and Assignment Routes */}
                                    <Route path="/courses/:courseId" element={<CourseView />} />
                                    <Route path="/courses/:courseId/lectures/:lectureId" element={<LectureView />} />
                                    <Route path="/courses/:courseId/assignments/:assignmentId" element={<AssignmentView />} />

                                    {/* Knowledge Base Routes */}
                                    <Route path="/knowledge-base" element={<KnowledgeBaseLanding />} />
                                    <Route path="/knowledge-base/:kbId" element={<KnowledgeBase />} />
                                </Route>

                                {/* Admin Routes */}
                                {renderRoutes(adminRoutes)}

                                {/* Catch all route */}
                                <Route path="*" element={<Navigate to="/dashboard" replace />} />
                            </Routes>
                            <ModalContainer />
                        </DropdownProvider>
                    </ModalProvider>
                </AuthProvider>
            </ThemeProvider>
        </Router>
    );
};

export default App; 