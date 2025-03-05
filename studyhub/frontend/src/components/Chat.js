import React, { useState } from 'react';

const Chat = ({ isOpen, setIsOpen }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');

    const toggleChat = () => {
        setIsOpen(!isOpen);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (newMessage.trim()) {
            const userMessage = { text: newMessage, sender: 'user' };
            setMessages([...messages, userMessage]);
            setNewMessage('');

            // Simulating AI response (Placeholder)
            setTimeout(() => {
                const aiResponse = { text: "I'm here to help! 😊", sender: 'bot' };
                setMessages((prevMessages) => [...prevMessages, aiResponse]);
            }, 1000);
        }
    };

    return (
        <>
            {/* Chat Panel */}
            <div
                className={`fixed top-0 right-0 h-screen w-[400px] bg-zinc-800 dark:bg-zinc-900 text-white transform transition-transform duration-300 ease-in-out ${
                    isOpen ? 'translate-x-0' : 'translate-x-full'
                } shadow-lg border-l border-zinc-600 dark:border-zinc-700 z-50`}
            >
                <div className="flex flex-col h-full">
                    {/* Header */}
                    <div className="p-4 bg-zinc-700 dark:bg-zinc-800 flex justify-between items-center border-b border-zinc-600 dark:border-zinc-700">
                        <h3 className="text-lg font-semibold text-white">StudyBot</h3>
                        <button onClick={toggleChat} className="text-zinc-400 hover:text-white">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-zinc-800 dark:bg-zinc-900">
                        {messages.length === 0 && (
                            <div className="text-zinc-400 text-center">
                                Hi! How can I assist you today? 🤖
                            </div>
                        )}

                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-lg p-3 ${
                                        message.sender === 'user'
                                            ? 'bg-zinc-600 dark:bg-zinc-700 text-white'
                                            : 'bg-zinc-700 dark:bg-zinc-600 text-white'
                                    }`}
                                >
                                    {message.text}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Input */}
                    <div className="p-4 border-t border-zinc-600 dark:border-zinc-700 bg-zinc-700 dark:bg-zinc-800">
                        <form onSubmit={handleSubmit} className="flex space-x-2">
                            <input
                                type="text"
                                value={newMessage}
                                onChange={(e) => setNewMessage(e.target.value)}
                                placeholder="Type your message..."
                                className="flex-1 px-4 py-2 bg-zinc-600 dark:bg-zinc-700 text-white placeholder-zinc-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-zinc-500"
                            />
                            <button
                                type="submit"
                                className="px-4 py-2 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 rounded-lg hover:bg-zinc-800 dark:hover:bg-zinc-100"
                            >
                                Send
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            {/* Chat Button */}
            <button
                onClick={toggleChat}
                className={`fixed bottom-6 right-6 p-4 rounded-full bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 shadow-lg hover:bg-zinc-800 dark:hover:bg-zinc-100 transition-all duration-200 z-40 ${
                    isOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'
                }`}
            >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
            </button>
        </>
    );
};

export default Chat; 