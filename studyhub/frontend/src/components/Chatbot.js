import React, { useState, useRef, useEffect } from 'react';
import { 
  PaperClipIcon, 
  ArrowUpIcon, 
  ClipboardDocumentIcon, 
  CheckIcon, 
  StopIcon,
  ChatBubbleOvalLeftEllipsisIcon, 
  XMarkIcon,
  BookmarkIcon,
  BookmarkSlashIcon,
  Squares2X2Icon,
} from '@heroicons/react/24/outline';

const dummyMessages = [
  { id: 1, text: "Hi! How can I help you today?", isBot: true, time: "10:00 AM" }
];

const Chatbot = ({isOpen, setIsOpen}) => {
  const [files, setFiles] = useState([]);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState(dummyMessages);
  const [copiedId, setCopiedId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [savedChats, setSavedChats] = useState([]);
  const [showSavedChats, setShowSavedChats] = useState(false);
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Load saved chats from localStorage
  useEffect(() => {
    const savedChatsData = localStorage.getItem('savedChats');
    if (savedChatsData) {
      setSavedChats(JSON.parse(savedChatsData));
    }
  }, []);

  // Save chats to localStorage when updated
  useEffect(() => {
    localStorage.setItem('savedChats', JSON.stringify(savedChats));
  }, [savedChats]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setTimeout(scrollToBottom, 100);
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    // Check file size (limit to 5MB per file)
    const validFiles = selectedFiles.filter(file => file.size <= 5 * 1024 * 1024);
    
    if (validFiles.length !== selectedFiles.length) {
      alert('Some files were not added because they exceed the 5MB limit.');
    }
    
    setFiles(prevFiles => [...prevFiles, ...validFiles]);
  };

  const handleRemoveFile = (fileToRemove) => {
    setFiles(files.filter(file => file !== fileToRemove));
  };

  const handleCopy = async (text, id) => {
    await navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSaveChat = () => {
    const chatId = Date.now().toString();
    const newSavedChat = {
      id: chatId,
      messages: messages,
      date: new Date().toLocaleString()
    };
    setSavedChats([...savedChats, newSavedChat]);
  };

  const handleDeleteSavedChat = (chatId) => {
    setSavedChats(savedChats.filter(chat => chat.id !== chatId));
  };

  const handleLoadSavedChat = (chat) => {
    setMessages(chat.messages);
    setShowSavedChats(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!message.trim() && files.length === 0) return;

    // Add user message
    const userMessageId = Date.now();
    const userMessage = {
      id: userMessageId,
      text: message,
      isBot: false,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      files: files.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type
      }))
    };

    setMessages([...messages, userMessage]);
    setMessage('');
    setFiles([]);
    setIsLoading(true);

    // Create a new AbortController
    abortControllerRef.current = new AbortController();

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const botMessage = {
        id: Date.now(),
        text: "I'm here to help! This is a simulated response. In a real implementation, this would be connected to your backend API.",
        isBot: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleStopResponse = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target.classList.contains('chatbot-backdrop')) {
      setIsOpen(false);
    }
  };

  // Format message text with line breaks
  const formatMessage = (text) => {
    return text.split('\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        {i !== text.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <>
      {/* Chat toggle button */}
      <button
        onClick={toggleChat}
        className={`fixed bottom-6 right-6 p-4 rounded-full bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 shadow-lg hover:bg-zinc-800 dark:hover:bg-zinc-100 transition-all duration-200 z-40 ${
          isOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'
        }`}
      >
        <ChatBubbleOvalLeftEllipsisIcon className="h-6 w-6" />
      </button>

      {/* Chatbot backdrop */}
      <div
        className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity duration-300 chatbot-backdrop ${
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={handleBackdropClick}
      >
        {/* Chatbot container */}
        <div
          className={`fixed bottom-0 right-0 w-full sm:w-[400px] md:w-[450px] h-[600px] max-h-[90vh] bg-white dark:bg-zinc-900 rounded-t-xl sm:rounded-xl shadow-xl transform transition-all duration-300 overflow-hidden z-50 sm:bottom-4 sm:right-4 ${
            isOpen ? 'translate-y-0' : 'translate-y-full sm:translate-y-8 opacity-0'
          }`}
        >
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b border-zinc-200 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-800">
            <div className="flex items-center">
              <h3 className="font-semibold text-zinc-900 dark:text-white">StudyBot</h3>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowSavedChats(!showSavedChats)}
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-200 dark:hover:bg-zinc-700"
              >
                <Squares2X2Icon className="h-5 w-5" />
              </button>
              <button
                onClick={handleSaveChat}
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-200 dark:hover:bg-zinc-700"
              >
                <BookmarkIcon className="h-5 w-5" />
              </button>
              <button
                onClick={toggleChat}
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-200 dark:hover:bg-zinc-700"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Saved Chats Panel */}
          {showSavedChats && (
            <div className="absolute inset-0 top-[57px] bg-white dark:bg-zinc-900 z-10 overflow-y-auto">
              <div className="p-4 border-b border-zinc-200 dark:border-zinc-700">
                <h3 className="font-semibold text-zinc-900 dark:text-white">Saved Conversations</h3>
              </div>
              {savedChats.length === 0 ? (
                <div className="p-4 text-center text-zinc-500 dark:text-zinc-400">
                  No saved conversations yet
                </div>
              ) : (
                <div className="divide-y divide-zinc-200 dark:divide-zinc-700">
                  {savedChats.map(chat => (
                    <div key={chat.id} className="p-4 hover:bg-zinc-100 dark:hover:bg-zinc-800">
                      <div className="flex justify-between items-start">
                        <button
                          onClick={() => handleLoadSavedChat(chat)}
                          className="text-left flex-1"
                        >
                          <p className="font-medium text-zinc-900 dark:text-white truncate">
                            {chat.messages[1]?.text.substring(0, 30) || "Conversation"}...
                          </p>
                          <p className="text-sm text-zinc-500 dark:text-zinc-400">{chat.date}</p>
                        </button>
                        <button
                          onClick={() => handleDeleteSavedChat(chat.id)}
                          className="p-1 text-zinc-500 hover:text-red-500 dark:text-zinc-400"
                        >
                          <BookmarkSlashIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 h-[calc(100%-130px)]">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.isBot ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg p-3 ${
                    msg.isBot
                      ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white'
                      : 'bg-zinc-900 dark:bg-white text-white dark:text-zinc-900'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 break-words">
                      {formatMessage(msg.text)}
                      
                      {/* Display files if any */}
                      {msg.files && msg.files.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {msg.files.map((file, index) => (
                            <div key={index} className="flex items-center text-xs p-1.5 rounded bg-zinc-200 dark:bg-zinc-700">
                              <PaperClipIcon className="h-3 w-3 mr-1" />
                              <span className="truncate">{file.name}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    {/* Copy button */}
                    <button
                      onClick={() => handleCopy(msg.text, msg.id)}
                      className="ml-2 p-1 opacity-0 group-hover:opacity-100 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded transition-opacity"
                    >
                      {copiedId === msg.id ? (
                        <CheckIcon className="h-4 w-4 text-green-500" />
                      ) : (
                        <ClipboardDocumentIcon className="h-4 w-4 text-zinc-500 dark:text-zinc-400" />
                      )}
                    </button>
                  </div>
                  <div className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                    {msg.time}
                  </div>
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-lg p-3 bg-zinc-100 dark:bg-zinc-800">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="h-2 w-2 rounded-full bg-zinc-400 dark:bg-zinc-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="h-2 w-2 rounded-full bg-zinc-400 dark:bg-zinc-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="h-2 w-2 rounded-full bg-zinc-400 dark:bg-zinc-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <button
                      onClick={handleStopResponse}
                      className="p-1 rounded text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30"
                    >
                      <StopIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="p-4 border-t border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800">
            <div className="flex items-end space-x-2">
              <div className="flex-1 bg-zinc-100 dark:bg-zinc-700 rounded-lg">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message..."
                  className="w-full bg-transparent p-3 max-h-32 focus:outline-none text-zinc-900 dark:text-white resize-none"
                  rows={1}
                />
                
                {/* Display selected files */}
                {files.length > 0 && (
                  <div className="px-3 pb-2 flex flex-wrap gap-2">
                    {files.map((file, index) => (
                      <div key={index} className="flex items-center text-xs p-1.5 rounded bg-zinc-200 dark:bg-zinc-600 text-zinc-900 dark:text-white">
                        <PaperClipIcon className="h-3 w-3 mr-1" />
                        <span className="truncate max-w-[100px]">{file.name}</span>
                        <button
                          onClick={() => handleRemoveFile(file)}
                          className="ml-1 text-zinc-500 hover:text-red-500"
                        >
                          <XMarkIcon className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="flex space-x-2">
                <label className="p-3 rounded-lg bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-700 dark:hover:bg-zinc-600 cursor-pointer">
                  <PaperClipIcon className="h-5 w-5 text-zinc-500 dark:text-zinc-400" />
                  <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
                <button
                  onClick={handleSubmit}
                  disabled={!message.trim() && files.length === 0}
                  className={`p-3 rounded-lg ${
                    !message.trim() && files.length === 0
                      ? 'bg-zinc-200 dark:bg-zinc-700 text-zinc-400 dark:text-zinc-500 cursor-not-allowed'
                      : 'bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 hover:bg-zinc-800 dark:hover:bg-zinc-100'
                  }`}
                >
                  <ArrowUpIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Chatbot; 