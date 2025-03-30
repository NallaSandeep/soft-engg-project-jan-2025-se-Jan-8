import axios from 'axios';
import { use } from 'react';

const API_BASE_URL = 'http://127.0.0.1:5010';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

let socket = null;

// Add response interceptor to handle errors
api.interceptors.response.use(
    (response) => {
        // If it's a blob response, return the whole response, not just the data
        if (response.config.responseType === 'blob') {
            return response;
        }
        return response.data;
    },
    (error) => {
        console.error('API Error:', {
            url: error.config?.url,
            method: error.config?.method,
            status: error.response?.status,
            data: error.response?.data,
            error: error.message
        });

        if (error.response) {
            // if (error.response.status === 401) {
            //     localStorage.removeItem('token');
            //     // window.location.href = '/login';
            // }
            return Promise.reject(error.response.data);
        }
        return Promise.reject(error);
    }
);

// studyAI API
export const chatAPI = {
    createChat: (user_id, personalResources) => api.post(`/chat/${user_id}/session`, { personalResources }),
    getChat: (id) => api.get(`/chat/session/${id}`),
    updateChat: (id, operations) => api.patch(`/chat/session/${id}`, {operations: [operations]}),
    getChats: (user_id) => api.get(`/chat/sessions?user_id=${user_id}`),
    reportMessage: (session_id, message_id) => api.post(`/chat/report/${session_id}`, { message_id }),
    // updateUser: (id, userData) => api.put(`/users/${id}`, userData),
    deleteChat: (id) => api.delete(`/chat/session/${id}`)
};

export const messageAPI = {
    createConnection: (sessionId) => {
        console.log(sessionId)
        socket = new WebSocket(`${API_BASE_URL.replace('https', 'wss')}/stream/chat/session/${sessionId}/message`);

        socket.onopen = () => console.log('WebSocket Connected');
        return socket;
        // socket.onmessage = (event) => {
        //     if (this.onMessageReceived) {
        //         this.onMessageReceived(JSON.parse(event.data));
        //     }
        // };
        // socket.onclose = () => console.log('WebSocket Disconnected');
        // socket.onerror = (error) => console.error('WebSocket Error:', error);
    },
    sendMessage: (socket, session_id, message) => {
        console.log(session_id)
        if (socket  && socket.readyState === WebSocket.OPEN) {
            return socket.send(JSON.stringify({ session_id, message }));
        }
        else {
            console.error('WebSocket not connected');
        }
    }
}


export const adminApi = {
    getChatSessions: () => {
        return api.get('/sessions');
    }
};

export default api; 