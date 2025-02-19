import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
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
        <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900">
            {/* <Sidebar user={user}/> */}
            <Navbar user={user}/>
            <main className="flex-1 container bg-zinc-100 dark:bg-zinc-900 py-4">
                <Outlet />
            </main>
            <Chat />
        </div>
    );
};

export default Layout;
