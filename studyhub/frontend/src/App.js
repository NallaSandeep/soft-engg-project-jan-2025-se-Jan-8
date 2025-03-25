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
import NotFound from './components/errors/NotFound';
import ServerError from './components/errors/ServerError';

// Student Components
import StudentDashboard from './components/student/Dashboard';
import StudentCourses from './components/student/MyCourses';
import AssignmentList from './components/assignments/AssignmentList';
import CourseView from './components/student/CourseView';
import LectureView from './components/student/LectureView';
import AssignmentView from './components/assignments/AssignmentView';
import PersonalResource from './components/personal/PersonalResource';
import PersonalResourcesLanding from './components/personal/PersonalResourcesLanding';

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
                                <Route element={<Layout />}>
                                    {/* Default redirect to student dashboard */}
                                    <Route path="/" element={<Navigate to="/student/dashboard" replace />} />
                                    
                                    {/* Redirect old dashboard to student dashboard */}
                                    <Route path="/dashboard" element={<Navigate to="/student/dashboard" replace />} />

                                    {/* Student Routes */}
                                    <Route path="/student">
                                        <Route path="dashboard" element={<StudentDashboard />} />
                                        <Route path="courses" element={<StudentCourses />} />
                                        <Route path="courses/:courseId" element={<CourseView />} />
                                        <Route path="courses/:courseId/lectures/:lectureId" element={<LectureView />} />
                                        <Route path="courses/:courseId/assignments/:assignmentId" element={<AssignmentView />} />
                                        <Route path="assignments" element={<AssignmentList />} />
                                        <Route path="personal-resources" element={<PersonalResourcesLanding />} />
                                        <Route path="personal-resources/:resourceId" element={<PersonalResource />} />
                                    </Route>

                                    {/* TA Routes */}
                                    {renderRoutes(taRoutes)}

                                    {/* Admin Routes */}
                                    {renderRoutes(adminRoutes)}

                                    {/* Catch all route */}
                                    <Route path="*" element={<Navigate to="/student/dashboard" replace />} />
                                </Route>

                                <Route path="/500" element={<ServerError />} />
                                <Route path="*" element={<NotFound />} />
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