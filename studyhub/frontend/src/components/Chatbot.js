import React, { useState, useRef, useEffect, use } from 'react';
import { 
  ArrowUpIcon, 
  ClipboardDocumentIcon, 
  CheckIcon, 
  StopIcon,
  FlagIcon,
  ChatBubbleLeftRightIcon,
  XMarkIcon,
  BookmarkIcon,
  BookmarkSlashIcon,
  Squares2X2Icon,
  PlusIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { chatAPI, messageAPI } from '../services/chatService';
import { personalApi } from '../services/apiService';
import { v4 as uuidv4 } from 'uuid';
import MarkdownIt from 'markdown-it';
const md = new MarkdownIt();

// const dummyMessages = [
//   { id: 1, text: "Hi! How can I help you today?", isBot: true, time: "10:00 AM" }
// ];

const Chatbot = ({ user, isOpen, setIsOpen, pageContext }) => {
  const [firstLoad, setFirstLoad] = useState(false);
  // const [chatSessionId, setChatSessionId] = useState(null);
  const [message, setMessage] = useState('');
  const [currResponse, setCurrResponse] = useState('');
  const [messages, setMessages] = useState([]);
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [reportedMessageId, setReportedMessageId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [savedChats, setSavedChats] = useState(null);
  const [showSavedChats, setShowSavedChats] = useState(false);
  const [showMentions, setShowMentions] = useState(false);
  const [savedChatId, setSavedChatId] = useState(null);
  const [mentionOptions] = useState([
    { id: 1, name: 'code', prefix: '@code' },
    { id: 2, name: 'explain', prefix: '@explain' },
    { id: 3, name: 'summary', prefix: '@summary' },
    { id: 4, name: 'faq', prefix: '@faq' },
  ]);
  const [mentionSearch, setMentionSearch] = useState('');
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  // const [personalResources, setPersonalResources] = useState([]);
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);
  const socket = useRef(null);
  const personalResources = useRef(null);
  const chatSessionID = useRef(null);

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

  const handleNewChat = async () => {
    // Create a new chat session
    try {
      // Wait for the chat session to be created
      const response = await chatAPI.createChat(user?.id, personalResources.current);
      console.log('Chat session created:', response.session_id);
      chatSessionID.current = response.session_id;
  
      // Create WebSocket connection after chatSessionId is set
      socket.current = messageAPI.createConnection(response.session_id);
      console.log('WebSocket connection established for session:', response.session_id);
      setMessages([]);
      setIsFirstMessage(true); 
    } catch (error) {
      console.error('Error creating chat session or WebSocket connection:', error);
    }

    // // Create websocket connection for sending and receiving messages
    // socket.current = messageAPI.createConnection(chatSessionId)

    // const defaultMessage = [
    //   { id: Date.now(), text: "Hi! How can I help you today?", isBot: true, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
    // ];
    // setMessages(defaultMessage);
  };

  const toggleChat = async () => {
    if (!firstLoad) {
      console.log('First load');
      setFirstLoad(true);
      const response = await personalApi.getResources();
      console.log('Personal resources:', response.data);
      personalResources.current = response.data;
      console.log(user)
      handleNewChat();
    }
    setIsOpen(!isOpen);
    setTimeout(scrollToBottom, 100);
  };


  const handleCopy = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(id);
      setTimeout(() => setCopiedMessageId(null), 800);
    } catch (error) {
      console.error('Failed to copy message:', error);
    }
  };

  const handleReportMessage = async (id) => {
    setReportedMessageId(id);
    setTimeout(() => setReportedMessageId(null), 800);
    // Add your report logic here
      try {
      chatAPI.reportMessage(chatSessionID.current, id).then(() => {
        console.log("Chat message reported:", id);
      }).catch((error) => {
        console.error(error);
      })}
      catch (error) {
      console.error(error);
    };
  }

  const handleSaveChat = () => {
    chatAPI.updateChat(chatSessionID.current, {op: "replace", path: "/is_bookmarked", value: true});
  
  // Show save animation
  setSavedChatId(chatSessionID.current);
  setTimeout(() => setSavedChatId(null), 800);
};

  const handleDeleteSavedChat = (chatId) => {
    setSavedChats(savedChats.filter(chat => chat.id !== chatId));
    chatAPI.updateChat(chatId, {op: "replace", path: "/is_bookmarked", value: false});
  };

  const handleLoadSavedChat = async (chat) => {
    return
    chatSessionID.current = chat.id;
    const response = await chatAPI.getChat(chat.id)
    console.log('Saved chat messages:', response.messages);

    const formattedMessages = response.messages?.map(msg => ({
      id: message_id.id || uuidv4(),
      text: msg.isBot ? md.render(msg.text) : msg.text,
      isBot: msg.user == 'bot',
      isMarkdown: msg.isBot,
      time: new Date(msg.timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }));
    setMessages(formattedMessages);
    setShowSavedChats(false);

    // Create WebSocket connection after chatSessionId is set
    socket.current = messageAPI.createConnection(chatSessionID.current);
    console.log('Saved Chat: WebSocket connection established for session:', chatSessionID.current);
  };

  const handleShowSavedChats = async () => {
    if (showSavedChats) {
      setShowSavedChats(false);
      return;
    }
    setShowSavedChats(true);
    try {
      const response = await chatAPI.getChats(user?.id);
      if (Array.isArray(response)) {
        const formattedChats = response
          .filter(chat => chat.is_bookmarked)
          .map(chat => {
            const date = new Date(chat.created_at);
            const formattedDate = new Intl.DateTimeFormat('en-US', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              hour12: true
            }).format(date);
  
            return {
              id: chat.session_id,
              name: chat.name,
              messages: Array.isArray(chat.messages) ? chat.messages : [],
              date: formattedDate,
              timestamp: date.getTime() // Add timestamp for sorting
            };
          })
          .sort((a, b) => b.timestamp - a.timestamp); // Sort by timestamp descending
  
        setSavedChats(formattedChats);
      } else {
        console.error('Expected array response from getChats:', response);
      }
    } catch (error) {
      console.error('Error fetching saved chats:', error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === '@' && message.trim().length === 0) {
      // Only show mentions if @ is at the start
      setShowMentions(true);
      setMentionSearch('');
    } else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === 'Escape') {
      setShowMentions(false);
    } else if (e.key === 'Backspace' && message === '@') {
      // Close mentions window when backspacing the @ symbol
      setShowMentions(false);
    }
  };

  const handleMessageChange = (e) => {
    setMessage(e.target.value);
    if (showMentions) {
      if (!e.target.value.startsWith('@')) {
        setShowMentions(false);
      }
      setMentionSearch(e.target.value.slice(1));
      const validCommands = mentionOptions.map(opt => opt.name);
        for (const cmd of validCommands) {
          if (e.target.value.slice(1).startsWith(cmd)) {
            setMentionSearch(cmd);
            break;
          }
      }
      }
  };

  async function handleSubmit() {
    if (!message.trim()) return;
    setShowMentions(false);    
    const userMessageId = uuidv4();
    const userMessage = {
      id: userMessageId,
      text: message,
      isBot: false,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    if (isFirstMessage) {
      // update the chatsession name with the user's first message
      chatAPI.updateChat(chatSessionID.current, {op: "replace", path: "/name", value: message.slice(0, 15)});
      setIsFirstMessage(false);
    }
    setMessages([...messages, userMessage]);
    setMessage('');
    setIsLoading(true);

    abortControllerRef.current = new AbortController();

    // Send message to the server
    let res = ''
    let message_id = ''
    messageAPI.sendMessage(socket.current, chatSessionID.current, message)
    setIsLoading(true);
    socket.current.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.type === 'start') {
        res = '';
      }
      if (response.type === 'chunk') {
        res += response.content;
        message_id = response.message_id
      }
    
      if (response.final) {
        const formattedText = md.render(res.trim());
        
        const botMessage = {
          id: message_id || uuidv4(),
          text: formattedText,
          isBot: true,
          isMarkdown: true,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
        setCurrResponse('');
        res = '';
        message_id = '';
      }
    };
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
        className={`fixed bottom-6 right-6 p-4 rounded-full bg-blue-900/85 dark:bg-blue-600/40 text-white dark:text-zinc-900 shadow-lg hover:bg-blue-800 dark:hover:bg-blue-900 transition-all duration-200 z-40 ${
          isOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'
        }`}
      >
        <ChatBubbleLeftRightIcon className="h-6 w-6 text-blue-200 dark:text-blue-400" />
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
           className={`fixed inset-y-0 right-0 w-full sm:w-[350px] md:w-[420px] bg-white dark:bg-zinc-900 shadow-xl transform transition-all duration-300 flex flex-col z-50 ${
            isOpen 
              ? 'translate-x-0' 
              : 'translate-x-full'
          }`}
        >
          {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-zinc-200 dark:border-zinc-700 relative z-20">
          {/* Left side - New Chat/Back Button */}
            {showSavedChats ? (
              <button
                onClick={() => setShowSavedChats(false)}
                title="Back to Chat"
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-500 dark:text-zinc-400 dark:hover:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
            ) : (
              <button
                onClick={handleNewChat}
                title="Start a New Chat"
                className="p-2 rounded-lg text-zinc-500 hover:text-blue-500 dark:text-zinc-400 dark:hover:text-blue-400 hover:bg-blue-100/40 dark:hover:bg-blue-900/30"
              >
                <PlusIcon className="h-5 w-5" />
              </button>
            )}

          {showSavedChats && (
            <p className='text-xs font-semibold text-zinc-800 dark:text-zinc-100'>Saved Conversations</p>
          )}

          {/* Right side buttons */}
          <div className="flex items-center space-x-2 z-10">
          {!showSavedChats && (
            <button
              onClick={handleShowSavedChats}
              title="View Saved Chats"
              className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-200 dark:hover:bg-zinc-700"
            >
              <Squares2X2Icon className="h-5 w-5" />
            </button>
          )}

            {!showSavedChats && messages.length > 0 && (
              <button
                onClick={handleSaveChat}
                title="Bookmark Chat"
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-200 dark:hover:bg-zinc-700"
              >
                {savedChatId ? (
                  <CheckIcon className="h-5 w-5 text-zinc-500 animate-fade-in" />
                ) : (
                  <BookmarkIcon className="h-5 w-5" />
                )}
              </button>
            )}

            <button
              onClick={toggleChat}
              title="Close Chat"
              className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-200 dark:hover:bg-zinc-700"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
          </div>
          {/* Saved Chats Panel */}
          {showSavedChats && (
            <div className="absolute inset-0 top-[57px] bg-white dark:bg-zinc-900 rounded-b-xl sm:rounded-b-xl z-10">
              {savedChats?.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-[calc(100%-57px)] text-center px-4">
                  <div className="w-12 h-12 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center mb-3">
                    <BookmarkIcon className="h-6 w-6 text-zinc-400 dark:text-zinc-500" />
                  </div>
                  <p className="text-sm text-zinc-500 dark:text-zinc-400">
                    No saved conversations yet
                  </p>
                </div>
              ) : (
                <div className="overflow-y-auto h-[calc(100%-57px)] mt-3">
                  {savedChats?.map(chat => (
                    <div 
                      key={chat.id} 
                      className="border-b border-zinc-200 dark:border-zinc-700 last:border-0"
                    >
                      <div className="flex items-start justify-between p-4 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
                        <button
                          onClick={() => handleLoadSavedChat(chat)}
                          className="flex-1 text-left"
                        >
                          <div className="flex items-start gap-3">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-zinc-900 dark:text-white truncate">
                                {chat.name || "Conversation"}...
                              </p>
                              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                {chat.date}
                              </p>
                            </div>
                          </div>
                        </button>
                        <button
                          onClick={() => handleDeleteSavedChat(chat.id)}
                          className="p-1 -m-1 text-zinc-400 hover:text-red-500 dark:text-zinc-500 dark:hover:text-red-400"
                          title="Remove from saved"
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
          {/* Messages Section */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm text-md">
          {messages.length === 0 && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-4">
                <div className="w-16 h-16 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center mb-4">
                  <ChatBubbleLeftRightIcon className="h-8 w-8 text-zinc-600 dark:text-zinc-300" />
                </div>
                <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">
                  Welcome to StudyBot
                </h3>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 max-w-sm mb-6">
                I'm here to help you with your studies. Ask me anything about your coursework, 
                or use @commands for specific tasks.
                </p>
                <div className="flex flex-wrap justify-center gap-2 max-w-md">
                  {mentionOptions.map(option => (
                    <button
                      key={option.id}
                      onClick={() => setMessage(option.prefix + ' ')}
                      className="px-4 py-2 text-xs font-semibold rounded-xl bg-blue-200/50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
                    >
                      {option.prefix}
                    </button>
                  ))}
                </div>
              </div>
            )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.isBot ? 'justify-start' : 'justify-end'}`}
            >
              <div
                className={`max-w-[85%] rounded-xl p-2.5 ${
                  msg.isBot
                    ? 'dark:bg-zinc-900 text-zinc-900 dark:text-white'
                    : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200'
                }`}
              >
                <div className="flex justify-between items-start">
                <div className="flex-1 break-words">
                  {msg.isMarkdown ? (
                    <div 
                      dangerouslySetInnerHTML={{ __html: msg.text }}
                      className="prose prose-sm dark:prose-invert max-w-none"
                    />
                  ) : (
                    formatMessage(msg.text)
                  )}
                </div>
                </div>
                
                {/* Message Footer */}
                <div className="flex justify-start items-center text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                  {/* {msg.time} */}
                  {msg.isBot && (
                    <div className="flex items-center space-x-2 ml-2">
                      <button
                        onClick={() => handleCopy(msg.text, msg.id)}
                        className="p-1 rounded text-zinc-400 hover:text-blue-500 dark:text-zinc-400 dark:hover:text-blue-400 relative"
                        title="Copy Message"
                      >
                        {copiedMessageId === msg.id ? (
                          <CheckIcon className="h-4 w-4 text-zinc-400 animate-fade-in" />
                        ) : (
                          <ClipboardDocumentIcon className="h-4 w-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleReportMessage(msg.id)}
                        className="p-1 rounded text-zinc-400 hover:text-red-500 dark:text-zinc-400 dark:hover:text-red-400 relative"
                        title="Report Message"
                      >
                        {reportedMessageId === msg.id ? (
                          <CheckIcon className="h-4 w-4 text-red-500 animate-fade-in" />
                        ) : (
                          <FlagIcon className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

            {/* Loading Animation */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-lg p-3 bg-white dark:bg-zinc-900">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="h-1 w-1 rounded-full bg-zinc-400 dark:bg-zinc-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="h-1 w-1 rounded-full bg-zinc-400 dark:bg-zinc-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="h-1 w-1 rounded-full bg-zinc-400 dark:bg-zinc-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <span className="text-xs text-zinc-500 dark:text-zinc-400"></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-zinc-200 dark:border-zinc-700">
            {/* Input and Send Button */}
            <div className="flex-1 items-center space-x-2 relative">
              <div className="flex rounded-lg relative items-center">
                <textarea
                  value={message}
                  onChange={handleMessageChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message..."
                  className="text-sm rounded-sm w-full flex-1 bg-zinc-100 dark:bg-zinc-800 p-3 pr-24 max-h-32 focus:outline-none focus:border-1 focus:border-zinc-300 text-zinc-900 dark:text-zinc-100 resize-none"
                  rows={2}
                />

                {/* Action Buttons Container */}
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center space-x-1">
  
                {/* Send Button */}
                <button
                  onClick={handleSubmit}
                  title="Send Message"
                  disabled={!message.trim()}
                  className={`p-2 rounded-lg ${
                    !message.trim()
                      ? 'text-zinc-400 dark:text-zinc-500 cursor-not-allowed'
                      : 'text-zinc-600 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-700'
                  }`}
                >
                  <ArrowUpIcon className="h-5 w-5" />
                </button>
              </div>

              {/* Mentions Dropdown */}
              {showMentions && (
                <div className="absolute bottom-full left-0 mb-1 w-48 bg-white dark:bg-zinc-800 rounded-sm shadow-lg border border-zinc-200 dark:border-zinc-700 overflow-hidden">
                  {mentionOptions
                    .filter(option => 
                      option.name.toLowerCase().includes(mentionSearch.toLowerCase())
                    )
                    .map(option => (
                      <button
                        key={option.id}
                        onClick={() => {
                          const lastAtIndex = message.lastIndexOf('@');
                          const newMessage = 
                            message.slice(0, lastAtIndex) + 
                            option.prefix + ' ' + 
                            message.slice(lastAtIndex + mentionSearch.length + 1);
                          setMessage(newMessage);
                          setShowMentions(false);
                        }}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-zinc-100 dark:hover:bg-zinc-700 text-zinc-900 dark:text-white"
                      >
                        {option.name}
                      </button>
                    ))}
                </div>
              )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Chatbot;