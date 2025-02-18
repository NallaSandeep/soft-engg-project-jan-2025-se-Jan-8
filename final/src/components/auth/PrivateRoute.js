import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

// Simulating authentication status
const getUser = () => {
    const email = sessionStorage.getItem("userEmail");
    const role = sessionStorage.getItem("userRole");

    return email && role ? { email, role } : null;
};

const PrivateRoute = ({ children, roles = [] }) => {
    const location = useLocation();
    const user = getUser();

    if (!user) {
        // Redirect to login page with return URL
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (roles.length > 0 && !roles.includes(user.role)) {
        // Redirect users to their respective dashboards
        const redirectPaths = {
            admin: "/admin/dashboard",
            student: "/student/dashboard",
            ta: "/ta/dashboard"
        };

        return <Navigate to={redirectPaths[user.role] || "/dashboard"} replace />;
    }

    return children;
};

export default PrivateRoute;
