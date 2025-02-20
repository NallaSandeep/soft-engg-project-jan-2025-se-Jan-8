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
  // const [isOpen, setIsOpen] = useState(false);
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
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setShowSavedChats(false);
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const validFiles = selectedFiles.filter(file => 
      file.type === 'text/plain' || file.type === 'application/pdf'
    );
    
    if (validFiles.length !== selectedFiles.length) {
      alert('Only .txt and .pdf files are allowed');
    }
    setFiles(prev => [...prev, ...validFiles]);
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
    const chatToSave = {
      id: Date.now(),
      messages: messages,
      timestamp: new Date().toLocaleString()
    };
    setSavedChats(prev => [...prev, chatToSave]);
  };

  const handleDeleteSavedChat = (chatId) => {
    setSavedChats(prev => prev.filter(chat => chat.id !== chatId));
  };

  const handleLoadSavedChat = (chat) => {
    setMessages(chat.messages);
    setShowSavedChats(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (isLoading) {
      abortControllerRef.current?.abort();
      setIsLoading(false);
      return;
    }
  
    if (message.trim() || files.length > 0) {
      const currentTime = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
  
      const userMessage = {
        id: messages.length + 1,
        text: message,
        isUser: true,
        time: currentTime
      };
      
      setMessages(prev => [...prev, userMessage]);
      setMessage('');
      setFiles([]);
      setIsLoading(true);
      scrollToBottom();
  
      abortControllerRef.current = new AbortController();
  
      setTimeout(() => {
        if (!abortControllerRef.current?.signal.aborted) {
          const botMessage = {
            id: messages.length + 2,
            text: "I understand your question. Let me help you with that...",
            isBot: true,
            time: new Date().toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })
          };
          setMessages(prev => [...prev, botMessage]);
          setIsLoading(false);
          scrollToBottom();
        }
      }, 3000);
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      setIsOpen(false);
    }
  };

  return (
    <>
    <div 
     onClick={handleBackdropClick}
    className={`fixed inset-0 bg-black/20 transition-opacity duration-300 z-[100]
      ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
      <div className={`absolute top-0 right-0 h-full w-[420px] 
    transition-all duration-300 transform bg-white dark:bg-zinc-800 
    shadow-2xl shadow-zinc-200/60 dark:shadow-black/20
    ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
  >
        <div className="flex flex-col h-full bg-zinc-50 dark:bg-zinc-800">
          <div className="px-3 py-4 flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-lg tracking-wide dark:text-zinc-50">
                StudyBot
              </h1>
              <button
                onClick={() => setShowSavedChats(!showSavedChats)}
                className="p-2 rounded-lg transition-colors
                  text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100
                  dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-700"
              >
                <Squares2X2Icon className="w-5 h-5" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              {messages.length > 1 && (
                <button
                  onClick={handleSaveChat}
                  className="p-2 rounded-lg transition-colors
                    text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100
                    dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-700"
                >
                  <BookmarkIcon className="w-5 h-5" />
                </button>
              )}
              <button 
                onClick={() => setIsOpen(false)}
                className="p-2 rounded-lg transition-colors
                  text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100
                  dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-700"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
          </div>

          {showSavedChats ? (
            <div className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
              {savedChats.length === 0 ? (
                <p className="text-center text-zinc-500 dark:text-zinc-400">
                  No saved chats yet
                </p>
              ) : (
                savedChats.map(chat => (
                  <div
                    key={chat.id}
                    className="p-4 rounded-lg border-1 border-zinc-200 dark:border-zinc-950 bg-zinc-100 dark:bg-zinc-900
                      hover:bg-zinc-50 dark:hover:bg-zinc-700/50 transition-colors
                      cursor-pointer group"
                    onClick={() => handleLoadSavedChat(chat)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <p className="text-sm text-zinc-900 dark:text-zinc-100 line-clamp-2">
                          {chat.messages[chat.messages.length - 1].text}
                        </p>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400">
                          {chat.timestamp}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteSavedChat(chat.id);
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded
                          text-zinc-400 hover:text-red-500 transition-all"
                      >
                        <BookmarkSlashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          ) : (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
                {messages.map((msg) => (
                  <div key={msg.id} 
                    className={`flex ${msg.isBot ? 'justify-start' : 'justify-end'}`}
                  >
                    <div className={`group relative max-w-[80%] rounded-lg px-3 py-2
                      ${msg.isBot ? 
                        'bg-zinc-200 dark:bg-zinc-700 text-zinc-800 font-medium dark:text-zinc-100' : 
                        'bg-zinc-100 dark:bg-zinc-950/30 text-zinc-950 dark:text-zinc-100'}`}
                    >
                      <button
                        onClick={() => handleCopy(msg.text, msg.id)}
                        className="absolute top-2 right-2 p-1 rounded opacity-0 
                          group-hover:opacity-100 transition-all duration-200
                          hover:bg-zinc-200 dark:hover:bg-zinc-600"
                      >
                        {copiedId === msg.id ? (
                          <CheckIcon className="w-4 h-4 text-zinc-300 dark:text-zinc-300" />
                        ) : (
                          <ClipboardDocumentIcon className="w-4 h-4 text-zinc-300 dark:text-zinc-300" />
                        )}
                      </button>
                      <p className="text-sm pr-6">{msg.text}</p>
                      <span className="text-[10px] mt-1 block text-zinc-400 dark:text-zinc-400">
                        {msg.time}
                      </span>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] rounded-lg px-4 py-2 bg-zinc-100 dark:bg-zinc-700">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce" />
                        <div className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce delay-100" />
                        <div className="w-2 h-2 rounded-full bg-zinc-400 animate-bounce delay-200" />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="p-4">
                {files.length > 0 && (
                  <div className="mb-3 flex gap-2 overflow-x-auto pb-2 no-scrollbar">
                    {files.map((file, index) => (
                      <div key={index} 
                        className="relative group p-2.5 rounded-lg flex-shrink-0 w-[120px] 
                          flex flex-col justify-between bg-zinc-200/50 dark:bg-zinc-700/50 
                          hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors duration-200"
                      >
                        <div className="flex items-start justify-between">
                          <PaperClipIcon className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
                          <button 
                            onClick={() => handleRemoveFile(file)}
                            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 
                              rounded-md hover:bg-zinc-300 dark:hover:bg-zinc-600"
                          >
                            <span className="sr-only">Remove file</span>
                            ✕
                          </button>
                        </div>
                        
                        <div className="mt-2">
                          <p className="text-xs truncate text-zinc-600 dark:text-zinc-300">
                            {file.name}
                          </p>
                          <p className="text-[10px] mt-1 text-zinc-400 dark:text-zinc-500">
                            {file.type.split('/')[1].toUpperCase()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="flex-1 chat-input flex flex-col rounded-sm border-1 border-zinc-400 dark:border-zinc-500 transition-all duration-200
                  bg-zinc-50 hover:bg-zinc-100 dark:bg-zinc-700/80 dark:hover:bg-zinc-700">
                  
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    className="flex-1 px-3 py-3 bg-transparent resize-none no-scrollbar
                      text-zinc-900 dark:text-zinc-100 
                      placeholder-zinc-400 dark:placeholder-zinc-500
                      outline-none text-sm leading-relaxed"
                  />
                  
                  <div className="flex items-center justify-between px-3 py-2">
                    <label className="cursor-pointer transition-colors
                      text-zinc-600 hover:text-zinc-700 
                      dark:text-zinc-400 dark:hover:text-zinc-300">
                      <PaperClipIcon className="w-5 h-5" />
                      <input 
                        type="file" 
                        onChange={handleFileChange} 
                        accept=".txt,.pdf" 
                        className="hidden"
                        multiple
                      />
                    </label>
                    
                    <button 
                      onClick={handleSubmit}
                      className={`transition-colors p-1 rounded-lg ${
                        isLoading 
                          ? 'text-red-600 hover:text-red-500 hover:bg-red-100 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-400/10'
                          : 'text-zinc-600 hover:text-orange-600 hover:bg-orange-100 dark:text-zinc-400 dark:hover:text-orange-400 dark:hover:bg-orange-400/10'
                      }`}
                    >
                      {isLoading ? (
                        <StopIcon className="w-5 h-5" />
                      ) : (
                        <ArrowUpIcon className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      
    </div>
    <button
        onClick={toggleChat}
        className={`fixed bottom-4 right-4 bg-orange-100 text-black p-3 
          rounded-full shadow-lg hover:bg-orange-50 transition-all duration-300 z-50
          ${isOpen ? 'opacity-0 translate-y-1 pointer-events-none' : 'opacity-100 translate-y-0'}`}
      >
        <ChatBubbleOvalLeftEllipsisIcon className="h-6 w-6" />
      </button>
    </>
  );
};

export default Chatbot;