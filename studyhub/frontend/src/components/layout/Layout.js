import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Navbar from './Navbar';
import Chatbot from '../Chatbot';

const Layout = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [isChatOpen, setIsChatOpen] = useState(false);

    // Redirect if no user
    useEffect(() => {
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    useEffect(() => {
        // Control body overflow when chat is open
        document.body.style.overflow = isChatOpen ? 'hidden' : 'auto';
        
        // Cleanup function
        return () => {
            document.body.style.overflow = 'auto';
        };
    }, [isChatOpen]);

    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900">
            <Navbar />
            <main className="container mx-auto px-4 py-8 min-h-screen">
                <Outlet />
            </main>
            {user && user.role === 'student' && (
                <Chatbot isOpen={isChatOpen} setIsOpen={setIsChatOpen} />
            )}
        </div>
    );
};

export default Layout; 