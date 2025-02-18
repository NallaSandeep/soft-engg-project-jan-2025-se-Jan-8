import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const RoleBasedRoute = ({ roles, children }) => {
    const { user } = useAuth();

    if (!roles.includes(user?.role)) {
        return <Navigate to="/dashboard" replace />;
    }

    return children;
};

export default RoleBasedRoute; 