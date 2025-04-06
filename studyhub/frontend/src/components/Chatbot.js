import React, { useState, useRef, useEffect, use } from 'react';
import { 
  ArrowUpIcon, 
  ClipboardDocumentIcon, 
  CheckIcon, 
  FlagIcon,
  ChatBubbleLeftRightIcon,
  XMarkIcon,
  BookmarkIcon,
  BookmarkSlashIcon,
  PlusIcon,
  ArrowLeftIcon,
  TrashIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

import { chatAPI, messageAPI } from '../services/chatService';
import { courseApi, personalApi } from '../services/apiService';
import { v4 as uuidv4 } from 'uuid';
import MarkdownIt from 'markdown-it';
import {Panel, PanelGroup, PanelResizeHandle} from 'react-resizable-panels';

const md = new MarkdownIt();

const Chatbot = ({ user, isOpen, setIsOpen, pageContext }) => {
  const [firstLoad, setFirstLoad] = useState(false);
  const [message, setMessage] = useState('');
  const [currResponse, setCurrResponse] = useState('');
  const [messages, setMessages] = useState([]);
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [reportedMessageId, setReportedMessageId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [savedChats, setSavedChats] = useState(null);
  const [showMentions, setShowMentions] = useState(false);
  const [savedChatId, setSavedChatId] = useState(null);
  const [mentionOptions] = useState([
    { id: 1, name: 'Course', prefix: '@Course' },
    { id: 2, name: 'FAQ', prefix: '@FAQ' },
    { id: 3, name: 'Notes', prefix: '@Notes' },
  ]);
  const [mentionSearch, setMentionSearch] = useState('');
  const [isFirstMessage, setIsFirstMessage] = useState(true);
  const [allChats, setAllChats] = useState([]);
  const [isFetchingChats, setIsFetchingChats] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [courses, setCourses] = useState([]);
  // Add new state for personal notes
  const [personalNotes, setPersonalNotes] = useState([]);
  const [loadingNotes, setLoadingNotes] = useState(false);
  // Add new state variables for context pills
  const [selectedContexts, setSelectedContexts] = useState([]);
  const [showContextMenu, setShowContextMenu] = useState(false);

  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);
  const socket = useRef(null);
  const personalResources = useRef(null);
  const chatSessionID = useRef(null);

  // Load the subscribed courses
  useEffect(() => {
    if (firstLoad) {
      fetchCourses();
    }
  }, [firstLoad]);

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

  const fetchCourses = async () => {
    try {
      const response = await courseApi.getCourses();
      console.log('Fetched courses:', response);
      if (response.success) {
        const formattedCourses = response.data.map(course => ({
          id: course.id,
          code: course.code,
          name: course.name
        }));
        setCourses(formattedCourses);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
    }
  };
  
  // Add context management functions
  const addContext = (context) => {
    // Always set just one context, replacing any existing ones
    setSelectedContexts([context]);
    setShowContextMenu(false);
  };

  const removeContext = (contextId) => {
    setSelectedContexts(selectedContexts.filter(c => c.id !== contextId));
  };

  const handleToggleSave = async (chatId, save) => {
    try {
      await chatAPI.updateChat(chatId, {
        op: "replace", 
        path: "/is_bookmarked", 
        value: save
      });
      
      setAllChats(prev => prev.map(chat => 
        chat.id === chatId 
          ? {...chat, isBookmarked: save}
          : chat
      ).sort((a, b) => {
        if (a.isBookmarked && !b.isBookmarked) return -1;
        if (!a.isBookmarked && b.isBookmarked) return 1;
        return b.timestamp - a.timestamp;
      }));
    } catch (error) {
      console.error('Error updating chat:', error);
    }
  };
  
  const handleDeleteChat = async (chatId) => {
    try {
      await chatAPI.deleteChat(chatId);
      setAllChats(prev => prev.filter(chat => chat.id !== chatId));
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  const handleShowHistory = async () => {
    if (showHistory) {
      setShowHistory(false);
      return;
    }
    setShowHistory(true);
    setIsFetchingChats(true);
  
    try {
      const response = await chatAPI.getChats(user?.id);
      if (Array.isArray(response)) {
        const formattedChats = response.map(chat => ({
          id: chat.session_id,
          name: chat.name,
          messages: Array.isArray(chat.messages) ? chat.messages : [],
          message_count: chat.message_count || 0,
          date: new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
          }).format(new Date(chat.created_at)),
          timestamp: new Date(chat.created_at).getTime(),
          isBookmarked: chat.is_bookmarked
        }));
  
        // Sort chats: bookmarked first, then by date
        const sortedChats = formattedChats.sort((a, b) => {
          if (a.isBookmarked && !b.isBookmarked) return -1;
          if (!a.isBookmarked && b.isBookmarked) return 1;
          return b.timestamp - a.timestamp;
        });
  
        setAllChats(sortedChats);
      }
    } catch (error) {
      console.error('Error fetching chats:', error);
    } finally {
      setIsFetchingChats(false);
    }
  };

  const handleNewChat = async () => {
    // Create a new chat session
    try {
      // Wait for the chat session to be created
      const response = await chatAPI.createChat(user?.id, courses);
      console.log('Chat session created:', response.session_id);
      chatSessionID.current = response.session_id;
  
      // Create WebSocket connection after chatSessionId is set
      socket.current = messageAPI.createConnection(response.session_id);
      console.log('WebSocket connection established for session:', response.session_id);
      setMessages([]);
      setIsFirstMessage(true); 
      setSelectedContexts([]); // Clear any selected contexts
    } catch (error) {
      console.error('Error creating chat session or WebSocket connection:', error);
    }
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
  setSavedChatId(chatSessionID.current);
  setTimeout(() => setSavedChatId(null), 800);
};

  const handleLoadSavedChat = async (chat) => {
    socket.current?.close(); // Close existing socket connection if any
    setMessages([]);
    chatSessionID.current = chat.id;
    chatAPI.getChat(chat.id).then((response) => {
      console.log('Loaded chat:', response);
      const formattedMessages = response.messages?.map(msg => ({
        id: msg.message_id || uuidv4(),
        text: msg.sender==='bot' ? md.render(msg.message) : msg.message,
        o_text: msg.sender==='bot' ? msg.message : msg.message,
        isBot: msg.sender === 'bot',
        isMarkdown:msg.sender === 'bot',
        time: new Date(msg.timestamp).toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      }));
      console.log('Formatted messages:', formattedMessages);
      setMessages(formattedMessages);
      setShowHistory(false);
      setIsFirstMessage(false);
      setTimeout(() => setSavedChatId(null), 800);
      setIsLoading(false);
    }).catch((error) => {
      console.error('Error loading chat:', error);
    });
    // Create WebSocket connection after chatSessionId is set
    socket.current = messageAPI.createConnection(chatSessionID.current);
    console.log('Saved Chat: WebSocket connection established for session:', chatSessionID.current);
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
      setShowContextMenu(false);
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
          if (e.target.value.slice(1).toLowerCase().startsWith(cmd.toLowerCase())) {
            setMentionSearch(cmd.toLowerCase());
            break;
          }
      }
      }
  };

  // Add a function to load personal notes
  const loadPersonalNotes = async () => {
    try {
      setLoadingNotes(true);
      const response = await personalApi.getResources();
      if (response?.data) {
        setPersonalNotes(response.data);
      }
    } catch (err) {
      console.error('Error loading personal notes:', err);
    } finally {
      setLoadingNotes(false);
    }
  };

  // Add this to useEffect
  useEffect(() => {
    // Load courses for the Course command
    fetchCourses();
    // Load personal notes for the Notes command
    loadPersonalNotes();
  }, []);

  // Add the addNotesContext function
  const addNotesContext = (note) => {
    addContext({
      id: uuidv4(),
      type: 'notes',
      resourceId: note.id,
      name: note.name,
      courseName: note.course?.name,
      courseCode: note.course?.code
    });
    setShowMentions(false);
  };

  async function handleSubmit() {
    if (!message.trim()) return;
    setShowMentions(false);
    setShowContextMenu(false);
    
    // Create context string for the API with corrected format
    let contextString = '';
    if (selectedContexts.length > 0) {
      contextString = selectedContexts.map(context => {
        if (context.type === 'course') {
          return `Course ${context.code}:`; // Add space after "Course"
        } else if (context.type === 'notes') {
          return `Note ${context.resourceId}:`; // Format as Note [ID]: for backend
        } else {
          return 'FAQ:'; // Keep FAQ format the same
        }
      }).join(' ') + ' ';
    }
    
    const userMessageId = uuidv4();
    const userMessage = {
      id: userMessageId,
      text: message,
      isBot: false,
      contexts: selectedContexts.map(c => ({...c})), // Store contexts for reference
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

    // Create the message with context directives prepended
    const messageWithContext = contextString + message;

    // Send message to the server
    let res = ''
    let message_id = ''
    messageAPI.sendMessage(socket.current, chatSessionID.current, messageWithContext)
    setIsLoading(true);
    if (!socket.current) {
      return
    } 
    socket.current.onmessage = (event) => {
      const response = JSON.parse(event.data);
      console.log(response)
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
          o_text: res.trim(),
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
    return text?.split('\n').map((line, i) => (
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

      <div className={`fixed inset-0 bg-black/50 backdrop-blur-md ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'} transition-opacity duration-500 z-40`}>

      <PanelGroup direction='horizontal' className={`fixed inset-0 z-50 ${isOpen ? 'translate-x-0' : 'translate-x-full'} transition-transform duration-500`}>
      {/* Chatbot backdrop */}
      <Panel
        className={`chatbot-backdrop`}
        onClick={handleBackdropClick}
      >
        </Panel>
        <PanelResizeHandle className="w-2 z-50" isVertical={true} />
        {/* Chatbot container */}
        <Panel defaultSize={35} minSize={35} className={`inset-0 right-0 top-0 bg-white dark:bg-zinc-900 shadow-xl transform transition-all flex flex-col`}>
          {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-zinc-200 dark:border-zinc-700 relative z-20">
          {/* Left side - New Chat/Back Button */}
            {showHistory ? (
              <button
                onClick={() => setShowHistory(false)}
                title="Back to Chat"
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-500 dark:text-zinc-400 dark:hover:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/50"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
            ) : (
              <button
                onClick={handleNewChat}
                title="Start a New Chat"
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-500 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-100 hover:text-black dark:hover:bg-zinc-800/50"
              >
                <PlusIcon className="h-5 w-5" />
              </button>
            )}

          {showHistory && (
            <p className='text-xs font-semibold text-zinc-800 dark:text-zinc-100'>Previous Conversations</p>
          )}

          {/* Right side buttons */}
          <div className="flex items-center space-x-2 z-10">
          {!showHistory && (
            <button
              onClick={handleShowHistory}
              title="View Saved Chats"
              className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800/50"
            >
              <ClockIcon className="h-5 w-5" />
            </button>
          )}

            {!showHistory && messages.length > 0 && (
              <button
                onClick={handleSaveChat}
                title="Bookmark Chat"
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800/50"
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
              className="p-2 rounded-lg text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-200 dark:hover:bg-zinc-800/50"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
          </div>
          {/* History Panel */}
          {showHistory && (
            <div className="absolute inset-0 top-[57px] bg-white dark:bg-zinc-900 rounded-b-xl sm:rounded-b-xl z-20">
              {allChats?.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-[calc(100%-57px)] text-center px-4">
                  <div className="w-12 h-12 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center mb-3">
                    <ChatBubbleLeftRightIcon className="h-6 w-6 text-zinc-400 dark:text-zinc-500" />
                  </div>
                  <p className="text-sm text-zinc-500 dark:text-zinc-400">
                    No conversations yet
                  </p>
                </div>
              ) : (
                <div className="overflow-y-auto h-full">
                  {allChats?.filter(chat => chat.message_count > 0).map(chat => (
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
                              <div className="flex items-center gap-2">
                                <p className="text-sm font-medium text-zinc-900 dark:text-white truncate">
                                  {chat.name || "Conversation"}...
                                </p>
                                {chat.isBookmarked && (
                                  <BookmarkIcon className="h-3.5 w-3.5 text-zinc-400 fill-zinc-400 dark:text-zinc-500 dark:fill-zinc-500" />
                                )}
                              </div>
                              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                                {chat.date}
                              </p>
                            </div>
                          </div>
                        </button>
                        <div className="flex items-center space-x-2">
                          {chat.isBookmarked ? (
                            <button
                              onClick={() => handleToggleSave(chat.id, false)}
                              className="p-1 text-zinc-400 hover:text-blue-500"
                              title="Remove from saved"
                            >
                              <BookmarkSlashIcon className="h-4 w-4" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handleToggleSave(chat.id, true)}
                              className="p-1 text-zinc-400 hover:text-blue-500"
                              title="Save conversation"
                            >
                              <BookmarkIcon className="h-4 w-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleDeleteChat(chat.id)}
                            className="p-1 text-zinc-400 hover:text-red-500"
                            title="Delete conversation"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
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
                      onClick={() => {
                        if (option.name === 'Course') {
                          setShowMentions(true);
                          setMentionSearch('course');  // lowercase to match the comparison
                        } else if (option.name === 'Notes') {
                          setShowMentions(true);
                          setMentionSearch('notes');  // lowercase to match the comparison
                        } else if (option.name === 'FAQ') {
                          // Add FAQ context directly
                          addContext({ id: uuidv4(), type: 'faq' });
                        }
                      }}
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
                className={`max-w-[85%] rounded-xl py-2.5 ${
                  msg.isBot
                    ? 'dark:bg-zinc-900 text-zinc-900 dark:text-white'
                    : 'bg-zinc-100 px-4 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200'
                }`}
              >
                {/* Show context pills for user messages if they exist */}
                {!msg.isBot && msg.contexts && msg.contexts.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {msg.contexts.map(context => (
                      <div 
                        key={context.id}
                        className="flex items-center bg-blue-100 dark:bg-blue-900/30 px-2 py-0.5 rounded-full text-blue-800 dark:text-blue-300 text-xs"
                      >
                        <span className="font-medium">
                          {context.type === 'course' ? `@Course: ${context.code}` : 
                           context.type === 'notes' ? `@Note: ${context.name}` : 
                           '@FAQ:'}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="flex justify-between items-start">
                <div className="flex-1 break-words">
                  {msg.isMarkdown ? (
                    <div 
                      dangerouslySetInnerHTML={{ __html: msg.text }}
                      className="prose prose-sm dark:prose-invert max-w-none overflow-x-auto"
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
                        onClick={() => handleCopy(msg.o_text, msg.id)}
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
                        <div className="h-1.5 w-1.5 rounded-full bg-zinc-400 dark:bg-zinc-500 opacity-75 animate-pulse"></div>
                        <div className="h-1.5 w-1.5 rounded-full bg-zinc-400 dark:bg-zinc-500 opacity-75 animate-pulse delay-75"></div>
                        <div className="h-1.5 w-1.5 rounded-full bg-zinc-400 dark:bg-zinc-500 opacity-75 animate-pulse delay-150"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-zinc-200 dark:border-zinc-700">
            {/* Context Pills */}
            <div className="flex flex-wrap items-center gap-2 mb-2 px-1">
              {/* Selected context pills */}
              {selectedContexts.map(context => (
                <div 
                  key={context.id} 
                  className="flex items-center bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded-full text-blue-800 dark:text-blue-300 text-xs"
                >
                  <span className="font-medium">
                    {context.type === 'course' ? `@Course: ${context.code}` : 
                     context.type === 'notes' ? `@Note: ${context.name}` : 
                     '@FAQ:'}
                  </span>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      removeContext(context.id);
                    }}
                    className="ml-1 text-blue-500 hover:text-blue-700 z-10"
                  >
                    <XMarkIcon className="h-3 w-3" />
                  </button>
                </div>
              ))}
              
              {/* Add context button */}
              <button 
                onClick={() => setShowContextMenu(!showContextMenu)}
                className="text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 p-1 rounded-full"
                title="Add context"
              >
                <span className="text-sm font-medium">@</span>
              </button>
              
              {/* Context menu */}
              {showContextMenu && (
                <div className="absolute left-4 bottom-20 bg-white dark:bg-zinc-800 shadow-lg rounded-md border border-zinc-200 dark:border-zinc-700 py-1 w-48 z-50">
                  <div className="text-xs font-medium text-zinc-500 dark:text-zinc-400 px-3 py-1">
                    Select Context
                  </div>
                  <button 
                    onClick={() => {
                      setShowMentions(true);
                      setShowContextMenu(false);
                      setMentionSearch('course');  // lowercase to match the comparison
                    }}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-700"
                  >
                    Course
                  </button>
                  <button 
                    onClick={() => {
                      setShowMentions(true);
                      setShowContextMenu(false);
                      setMentionSearch('notes');  // show notes selection
                    }}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-700"
                  >
                    Notes
                  </button>
                  <button 
                    onClick={() => addContext({ id: uuidv4(), type: 'faq' })}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-700"
                  >
                    FAQ
                  </button>
                </div>
              )}
            </div>

            {/* Input and Send Button */}
            <div className="flex-1 items-center space-x-2 relative">
              <div className="flex rounded-lg relative items-center">
                <textarea
                  value={message}
                  onChange={handleMessageChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message..."
                  className="text-sm rounded-sm w-full flex-1 bg-zinc-100 dark:bg-zinc-800 p-3 pr-24 max-h-32 text-zinc-900 dark:text-zinc-100 resize-none focus:ring-1 focus:ring-zinc-400 focus:outline-none dark:focus:ring-zinc-500 ring-1 ring-zinc-300 dark:ring-zinc-700"
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
                      : 'text-blue-600 dark:text-blue-400 hover:bg-blue-200/50 dark:hover:bg-blue-800/30'
                  }`}
                >
                  <ArrowUpIcon className="h-5 w-5" />
                </button>
              </div>

              {/* Mentions Menu */}
              <div className={`absolute bottom-full left-0 mb-1 ${showMentions ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0 pointer-events-none'} transform transition-all duration-200 z-50`}>
                {mentionSearch.toLowerCase() === 'course' ? (
                  // Course Selection Menu - Modified for pill UI
                  <div className="w-64 bg-white dark:bg-zinc-800 rounded-sm shadow-lg border border-zinc-200 dark:border-zinc-700">
                    {courses.length === 0 ? (
                      <div className="p-4 text-sm text-zinc-500 dark:text-zinc-400 text-center">
                        No courses available
                      </div>
                    ) : (
                      courses.map(course => (
                        <button
                          key={course.id}
                          onClick={() => {
                            // Instead of modifying message text, add as context pill
                            addContext({
                              id: uuidv4(),
                              type: 'course',
                              code: course.code,
                              name: course.name
                            });
                            setShowMentions(false);
                          }}
                          className="w-full px-4 py-2 text-left hover:bg-zinc-100 dark:hover:bg-zinc-700"
                        >
                          <div className="flex flex-col">
                            <span className="text-sm font-medium text-zinc-900 dark:text-white">
                              {course.code}
                            </span>
                            <span className="text-xs text-zinc-500 dark:text-zinc-400">
                              {course.name}
                            </span>
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                ) : mentionSearch.toLowerCase() === 'notes' ? (
                  // Personal Notes Selection Menu
                  <div className="w-80 bg-white dark:bg-zinc-800 rounded-sm shadow-lg border border-zinc-200 dark:border-zinc-700 max-h-96 overflow-y-auto">
                    {loadingNotes ? (
                      <div className="p-4 text-sm text-zinc-500 dark:text-zinc-400 text-center">
                        Loading your notes...
                      </div>
                    ) : personalNotes.length === 0 ? (
                      <div className="p-4 text-sm text-zinc-500 dark:text-zinc-400 text-center">
                        No personal notes available
                      </div>
                    ) : (
                      personalNotes.map(note => (
                        <button
                          key={note.id}
                          onClick={() => addNotesContext(note)}
                          className="w-full px-4 py-3 text-left hover:bg-zinc-100 dark:hover:bg-zinc-700 border-b border-zinc-200 dark:border-zinc-700"
                        >
                          <div className="flex flex-col">
                            <span className="text-sm font-medium text-zinc-900 dark:text-white">
                              {note.name}
                            </span>
                            <div className="flex items-center justify-between mt-1">
                              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                                {note.course?.code}: {note.course?.name}
                              </span>
                              <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 px-2 py-0.5 rounded">
                                {note.files?.length || 0} files
                              </span>
                            </div>
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                ) : (
                  // Primary Commands Menu
                  <div className="w-48 bg-white dark:bg-zinc-800 rounded-sm shadow-lg border border-zinc-200 dark:border-zinc-700">
                    {mentionOptions
                      .filter(option => 
                        option.name.toLowerCase().includes(mentionSearch.toLowerCase())
                      )
                      .map(option => (
                        <button
                          key={option.id}
                          onClick={() => {
                            if (option.name === 'Course') {
                              setMentionSearch('course');
                              return;
                            } else if (option.name === 'Notes') {
                              setMentionSearch('notes');
                              return;
                            }
                            // Add as context pill instead of text, replacing any existing contexts
                            setSelectedContexts([]);
                            addContext({
                              id: uuidv4(),
                              type: 'faq'
                            });
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
        </Panel>
      </PanelGroup>
      </div>
    </>
  );
};

export default Chatbot;