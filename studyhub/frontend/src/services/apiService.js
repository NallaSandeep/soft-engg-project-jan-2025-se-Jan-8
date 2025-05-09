import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        // Remove trailing slashes from the URL
        config.url = config.url.replace(/\/+$/, '');
        
        // Debug log for requests
        console.log('API Request:', {
            url: config.url,
            method: config.method,
            headers: config.headers
        });
        
        return config;
    },
    (error) => {
        console.error('Request Error:', error);
        return Promise.reject(error);
    }
);

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
            error: error.message,
            requestData: error.config?.data ? JSON.parse(error.config.data) : null
        });

        if (error.response) {
            // Handle token expiration
            if (error.response.status === 401) {
                localStorage.removeItem('token');
                // window.location.href = '/login';
            }
            return Promise.reject(error.response.data);
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authApi = {
    login: (credentials) => api.post('/auth/login', credentials),
    register: (userData) => api.post('/auth/register', userData),
    getCurrentUser: () => api.get('/auth/verify-token'),
    updateProfile: (userData) => api.put('/auth/profile', userData),
    changePassword: (passwords) => api.post('/auth/change-password', passwords)
};

// Course API
export const courseApi = {
    getCourses: () => api.get('/courses'),
    getCourse: (id) => api.get(`/courses/${id}`),
    createCourse: (courseData) => api.post('/courses', courseData),
    updateCourse: (id, courseData) => api.put(`/courses/${id}`, courseData),
    deleteCourse: (id) => api.delete(`/courses/${id}`),
    getCourseContent: (courseId) => api.get(`/courses/${courseId}/content`),
    enrollStudent: (courseId, studentId, role) => api.post(`/courses/enroll/`, { courseId, studentId, role }),
    unenrollStudent: (courseId, studentId) => api.delete(`/courses/${courseId}/enroll/${studentId}`),
    getEnrolledStudents: (courseId) => api.get(`/courses/${courseId}/students`),
    // Week management
    getAllWeeks: () => api.get('/courses/weeks'),
    getWeeks: (courseId) => api.get(`/courses/${courseId}/weeks`),
    createWeek: (courseId, weekData) => api.post(`/courses/${courseId}/weeks`, weekData),
    updateWeek: (courseId, weekId, weekData) => api.put(`/courses/${courseId}/weeks/${weekId}`, weekData),
    deleteWeek: (courseId, weekId) => api.delete(`/courses/${courseId}/weeks/${weekId}`),
    // Lecture management
    getLectures: (weekId) => api.get(`/courses/weeks/${weekId}/lectures`),
    getLectureContent: (lectureId) => api.get(`/courses/lectures/${lectureId}/content`),
    getLecturePdf: (lectureId) => api.get(`/courses/lectures/${lectureId}/pdf`, {
        responseType: 'blob',
        headers: {
            'Accept': 'application/pdf',
            'Content-Type': 'application/pdf'
        },
        withCredentials: true
    }),
    createLecture: (weekId, lectureData) => {
        console.log(`Creating lecture for week ${weekId}:`, lectureData);
        return api.post(`/courses/weeks/${weekId}/lectures`, lectureData);
    },
    updateLecture: (lectureId, lectureData) => api.put(`/courses/lectures/${lectureId}`, lectureData),
    deleteLecture: (lectureId) => api.delete(`/courses/lectures/${lectureId}`),
    uploadLecturePdf: (lectureId, formData) => api.post(`/courses/lectures/${lectureId}/pdf`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    }),
    // Assignment management
    getAssignments: (courseId) => api.get(`/courses/${courseId}/assignments`),
    createAssignment: (weekId, assignmentData) => api.post(`/courses/weeks/${weekId}/assignments`, assignmentData),
    updateAssignment: (assignmentId, assignmentData) => api.put(`/courses/assignments/${assignmentId}`, assignmentData),
    deleteAssignment: (assignmentId) => api.delete(`/courses/assignments/${assignmentId}`),
    markLectureCompleted: (lectureId) => api.post(`/courses/lectures/${lectureId}/progress`),
    getCourseProgress: (courseId) => api.get(`/courses/${courseId}/progress`),
};

// User API
export const userApi = {
    getUsers: () => api.get('/users'),
    getUser: (id) => api.get(`/users/${id}`),
    createUser: (userData) => api.post('/users', userData),
    updateUser: (id, userData) => api.put(`/users/${id}`, userData),
    deleteUser: (id) => api.delete(`/users/${id}`)
};

// Resource API
export const resourceApi = {
    getResources: (courseId) => api.get(`/courses/${courseId}/resources`),
    getResource: (courseId, resourceId) => api.get(`/courses/${courseId}/resources/${resourceId}`),
    createResource: (courseId, resourceData) => api.post(`/courses/${courseId}/resources`, resourceData),
    updateResource: (courseId, resourceId, resourceData) => api.put(`/courses/${courseId}/resources/${resourceId}`, resourceData),
    deleteResource: (courseId, resourceId) => api.delete(`/courses/${courseId}/resources/${resourceId}`),
    uploadFile: (courseId, formData) => api.post(`/courses/${courseId}/resources/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
};

// Progress API
export const progressApi = {
    getStudentProgress: (courseId, studentId) => api.get(`/courses/${courseId}/progress/${studentId}`),
    getClassProgress: (courseId) => api.get(`/courses/${courseId}/progress`),
    updateProgress: (courseId, studentId, progressData) => api.put(`/courses/${courseId}/progress/${studentId}`, progressData)
};

// Assignment API
export const assignmentApi = {
    // Get all assignments (admin/teacher view)
    getAssignments: (filters = {}) => {
        const params = new URLSearchParams();
        if (filters.course_id) params.append('course_id', filters.course_id);
        if (filters.type && filters.type !== 'All Types') params.append('type', filters.type.toLowerCase());
        if (filters.status && filters.status !== 'All Status') params.append('status', filters.status.toLowerCase());
        if (filters.search) params.append('search', filters.search);
        if (filters.week_id) params.append('week_id', filters.week_id);
        if (filters.page) params.append('page', filters.page);
        if (filters.limit) params.append('limit', filters.limit);
        return api.get(`/assignments?${params.toString()}`);
    },

    // Get assignments for a week
    getWeekAssignments: (weekId) => api.get(`/courses/weeks/${weekId}/assignments`),

    // Get all assignments for a student (across all courses)
    getStudentAssignments: () => api.get('/assignments/student/assignments'),

    // Get a specific assignment
    getAssignment: (assignmentId) => api.get(`/assignments/${assignmentId}`),

    // Submit an assignment
    submitAssignment: (assignmentId, submissionData) => api.post(`/assignments/${assignmentId}/submit`, submissionData),

    // Get student's submissions for an assignment
    getSubmissions: (assignmentId) => api.get(`/assignments/${assignmentId}/submissions`),

    // Get correct answers for an assignment (only available under specific conditions)
    getCorrectAnswers: (assignmentId) => api.get(`/assignments/${assignmentId}/correct-answers`),

    // For TAs: Create an assignment
    createAssignment: (weekId, assignmentData) => api.post(`/courses/weeks/${weekId}/assignments`, assignmentData),

    // For TAs: Update an assignment
    updateAssignment: (assignmentId, assignmentData) => api.put(`/assignments/${assignmentId}`, assignmentData),

    // For TAs: Delete an assignment
    deleteAssignment: (assignmentId) => api.delete(`/assignments/${assignmentId}`),

    // For TAs: Add questions to assignment
    addQuestions: (assignmentId, questionIds) => api.post(`/assignments/${assignmentId}/questions`, { question_ids: questionIds }),

    // For TAs: Remove question from assignment
    removeQuestion: (assignmentId, questionId) => api.delete(`/assignments/${assignmentId}/questions/${questionId}`),

    // For TAs: Get questions in an assignment
    getAssignmentQuestions: (assignmentId) => api.get(`/assignments/${assignmentId}/questions`),

    // For TAs: Update question order in assignment
    updateQuestionOrder: (assignmentId, questionOrders) => api.put(`/assignments/${assignmentId}/questions/order`, { orders: questionOrders })
};

// Admin API
export const adminApi = {
    getDashboardStats: () => api.get('/admin/dashboard/stats'),
    getSystemLogs: () => api.get('/admin/logs'),
    getUserActivity: () => api.get('/admin/user-activity'),
    getSystemHealth: () => api.get('/admin/health'),
    manageRoles: (userId, roleData) => api.put(`/admin/users/${userId}/roles`, roleData),
    getAuditLogs: () => api.get('/admin/audit-logs')
};

// TA API
export const taApi = {
    getDashboardStats: () => api.get('/ta/dashboard/stats')
};

// Question Bank API
export const questionBankApi = {
    // List questions with filters
    getQuestions: (filters = {}) => {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.type) params.append('type', filters.type);
        if (filters.difficulty) params.append('difficulty', filters.difficulty);
        if (filters.course_id) params.append('course_id', filters.course_id);
        if (filters.week_id) params.append('week_id', filters.week_id);
        if (filters.lecture_id) params.append('lecture_id', filters.lecture_id);
        if (filters.page) params.append('page', filters.page);
        if (filters.limit) params.append('limit', filters.limit);
        return api.get(`/question-bank/questions?${params.toString()}`);
    },

    // Get a specific question
    getQuestion: (questionId) => api.get(`/question-bank/questions/${questionId}`),

    // Create a question
    createQuestion: (questionData) => api.post('/question-bank/questions', questionData),

    // Update a question
    updateQuestion: (questionId, questionData) => api.put(`/question-bank/questions/${questionId}`, questionData),

    // Delete a question
    deleteQuestion: (questionId) => api.delete(`/question-bank/questions/${questionId}`),

    // Batch create questions
    batchCreateQuestions: (questionsData) => api.post('/question-bank/questions/batch', questionsData)
};


// Personal Resources API
export const personalApi = {
    getResources: () => api.get('/personal-resources'),
    getResource: (id) => api.get(`/personal-resources/${id}`),
    createResource: (resourceData) => api.post('/personal-resources', resourceData),
    updateResource: (id, resourceData) => api.put(`/personal-resources/${id}`, resourceData),
    deleteResource: (id) => api.delete(`/personal-resources/${id}`),
    uploadFile: (formData) => api.post('/personal-resources/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    downloadFile: (resourceId, fileId) => api.get(`/personal-resources/${resourceId}/files/${fileId}/download`, {
        responseType: 'blob',
        headers: {
            'Accept': 'application/octet-stream'
        }
    }),
    getResourceFiles: (resourceId) => api.get(`/personal-resources/${resourceId}/files`),
    deleteFile: (resourceId, fileId) => api.delete(`/personal-resources/${resourceId}/files/${fileId}`),
    updateNotes: (resourceId, notes) => api.put(`/personal-resources/${resourceId}/notes`, { notes }),
    shareResource: (resourceId, userData) => api.post(`/personal-resources/${resourceId}/share`, userData),
    unshareResource: (resourceId, userId) => api.delete(`/personal-resources/${resourceId}/share/${userId}`),
    createPersonalResource: (resourceData) => api.post('/personal-resources', resourceData),
    addFile: (resourceId, fileData) => {
        const formData = new FormData();
        if (fileData instanceof File) {
            formData.append('file', fileData);
        } else {
            // Handle text note
            formData.append('content', fileData.content);
            formData.append('name', fileData.name);
            formData.append('type', fileData.type);
        }
        return api.post(`/personal-resources/${resourceId}/files`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    }
};