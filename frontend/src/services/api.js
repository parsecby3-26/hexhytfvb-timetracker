import axios from 'axios';

// Ensure this matches your Render URL in Vercel Environment Variables
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://timetracker-api-m8k7.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  // Corrected path and data mapping
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response; 
  },
  register: (data) => api.post('/auth/register', data),
  verifyEmail: (token) => api.get(`/auth/verify-email?token=${token}`),
  resendVerification: (email) => api.post('/auth/resend-verification', null, { params: { email } }),
  requestPasswordReset: (email) => api.post('/auth/request-password-reset', { email }),
  resetPassword: (token, newPassword) => api.post('/auth/reset-password', { token, new_password: newPassword }),
  verifyFirstLogin: (data) => api.post('/auth/verify-first-login', data),
  // Corrected path
  getCurrentUser: () => api.get('/users/me'),
};

// Users API
export const usersAPI = {
  list: (params) => api.get('/users', { params }),
  get: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  updateRoles: (id, roles) => api.put(`/users/${id}/roles`, roles),
  getManagers: () => api.get('/users/managers/list'),
  resetPassword: (id, newPassword) => api.post(`/users/${id}/reset-password`, { new_password: newPassword }),
};

// Projects API
export const projectsAPI = {
  // Removed redundant /projects/projects
  list: (params) => api.get('/projects', { params }),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
  getMembers: (id) => api.get(`/projects/${id}/members`),
  addMember: (id, data) => api.post(`/projects/${id}/members`, data),
  removeMember: (projectId, userId) => api.delete(`/projects/${projectId}/members/${userId}`),
};

// Time Entries API
export const timeEntriesAPI = {
  // Removed redundant /time-entries/time-entries
  list: (params) => api.get('/time-entries', { params }),
  get: (id) => api.get(`/time-entries/${id}`),
  create: (data) => api.post('/time-entries', data),
  update: (id, data) => api.put(`/time-entries/${id}`, data),
  delete: (id) => api.delete(`/time-entries/${id}`),
  approve: (id, data) => api.post(`/time-entries/${id}/approve`, data),
  resubmit: (id, data) => api.post(`/time-entries/${id}/resubmit`, data),
  getPendingApprovals: (params) => api.get('/time-entries/pending/approvals', { params }),
};

// Reports API
export const reportsAPI = {
  getSummary: (params) => api.get('/reports/summary', { params }),
  getDaily: (params) => api.get('/reports/daily', { params }),
  getByReportingArea: (params) => api.get('/reports/by-reporting-area', { params }),
  getUserReport: (userId, params) => api.get(`/reports/user/${userId}`, { params }),
};

// Notifications API
export const notificationsAPI = {
  getNotifications: () => api.get('/notifications'),
  markAsRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllAsRead: () => api.post('/notifications/read-all'),
};

export const importAPI = {
  users: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/users/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  projects: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/projects/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const supportAPI = {
  submitFeedback: (data) => api.post('/support/feedback', data),
};

export default api;