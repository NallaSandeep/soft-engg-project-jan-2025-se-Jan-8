import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const PrivateRoute = ({ children, roles = [] }) => {
    const { user, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-gray-600">Loading...</div>
            </div>
        );
    }

    if (!user) {
        // Redirect to login page with return url
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (roles.length > 0 && !roles.includes(user.role)) {
        // Redirect to appropriate dashboard based on user role
        let redirectPath;
        switch (user.role) {
            case 'admin':
                redirectPath = '/admin/dashboard';
                break;
            case 'ta':
                redirectPath = '/ta/dashboard';
                break;
            case 'student':
                redirectPath = '/student/dashboard';
                break;
            default:
                redirectPath = '/dashboard';
        }
        return <Navigate to={redirectPath} replace />;
    }

    return children;
};

export default PrivateRoute; 