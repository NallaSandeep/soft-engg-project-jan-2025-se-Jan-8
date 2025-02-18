import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import Chat from '../Chat';

const Layout = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const email = sessionStorage.getItem("userEmail");
        const role = sessionStorage.getItem("userRole");

        if (email && role) {
            setUser({ email, role });
        } else {
            navigate('/login');
        }
    }, [navigate]);

    return (
        <div className="min-h-screen bg-dark text-white">
            <Navbar />
            <main className="flex-1 container py-4">
                <Outlet />
            </main>
            <Chat />
        </div>
    );
};

export default Layout;
