import React, { useState } from 'react';

const Chat = () => {
    const [isOpen, setIsOpen] = useState(false);
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
                className={`fixed top-0 right-0 h-screen w-[400px] bg-gray-900 text-white transform transition-transform duration-300 ease-in-out ${
                    isOpen ? 'translate-x-0' : 'translate-x-full'
                } shadow-lg border-l border-yellow-500`}
            >
                <div className="flex flex-col h-full">
                    {/* Header */}
                    <div className="p-4 bg-gray-800 flex justify-between items-center border-b border-yellow-500">
                        <h3 className="text-lg font-semibold text-yellow-400">StudyBot</h3>
                        <button onClick={toggleChat} className="text-gray-400 hover:text-yellow-400">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-800">
                        {messages.length === 0 && (
                            <div className="text-gray-400 text-center">
                                Hi! How can I assist you today? 🤖
                            </div>
                        )}
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-lg px-4 py-2 shadow ${
                                        message.sender === 'user'
                                            ? 'bg-yellow-500 text-black'
                                            : 'bg-gray-700 text-white'
                                    }`}
                                >
                                    {message.text}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Input */}
                    <div className="p-4 bg-gray-900 border-t border-yellow-500">
                        <form onSubmit={handleSubmit} className="flex space-x-2">
                            <input
                                type="text"
                                value={newMessage}
                                onChange={(e) => setNewMessage(e.target.value)}
                                placeholder="Type a message..."
                                className="flex-1 px-4 py-2 bg-gray-700 text-white border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
                            />
                            <button type="submit" className="p-2 text-yellow-400 hover:text-yellow-500">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                                </svg>
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            {/* Chat Toggle Button */}
            <button
                onClick={toggleChat}
                className="fixed bottom-4 right-4 bg-yellow-500 text-black p-3 rounded-full shadow-lg hover:bg-yellow-600 transition-colors z-50"
            >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
            </button>
        </>
    );
};

export default Chat;
