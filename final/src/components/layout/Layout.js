import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import Chat from '../Chat';
import Chatbot from '../Chatbot';

const Layout = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [isChatOpen, setIsChatOpen] = useState(false);

    useEffect(() => {
        const email = sessionStorage.getItem("userEmail");
        const role = sessionStorage.getItem("userRole");

        if (email && role) {
            setUser({ email, role });
        } else {
            navigate('/login');
        }
    }, [navigate]);

    useEffect(() => {
        if (isChatOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
        }

        // Cleanup function
        return () => {
            document.body.style.overflow = 'auto';
        };
    }, [isChatOpen]);

    // const handleMainClick = (e) => {
    //     if (isChatOpen && !e.target.closest('.chatbot-container')) {
    //         setIsChatOpen(false);
    //     }
    // };

    return (
        <div className="min-h-screen bg-zinc-100 dark:bg-zinc-900">
            <Navbar user={user}/>
            <main className="flex-1 container bg-zinc-100 dark:bg-zinc-900 py-4">
                <Outlet />
            </main>
            <Chatbot isOpen={isChatOpen} setIsOpen={setIsChatOpen}/>
        </div>
    );
};

export default Layout;