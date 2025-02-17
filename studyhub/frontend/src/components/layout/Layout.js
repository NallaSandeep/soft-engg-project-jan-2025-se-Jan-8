import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Navbar from './Navbar';
import Chat from '../Chat';

const Layout = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    // Redirect if no user
    React.useEffect(() => {
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    return (
        <div className="min-h-screen bg-white">
            <Navbar />
            <main className="flex-1">
                <Outlet />
            </main>
            <Chat />
        </div>
    );
};

export default Layout; 