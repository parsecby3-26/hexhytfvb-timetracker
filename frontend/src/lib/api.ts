import axios from 'axios';

const API_BASE = "https://timetracker-api-m8k7.onrender.com/api";

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to attach the JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authApi = {
  login: async (email, password) => {
    // Corrected: Removed the double '/auth/auth'
    const result = await api.post('/auth/login', { email, password });
    
    // Mapping the successful backend response to your frontend store
    return {
      profile: {
        id: result.data.data.profile.id,
        name: result.data.data.profile.name,
        email: result.data.data.profile.email,
        roles: result.data.data.profile.roles
      },
      token: result.data.data.token
    };
  },
  
  register: async (userData) => {
    const result = await api.post('/auth/register', userData);
    return result.data;
  },

  me: async () => {
    // Corrected: Removed the double '/users/users'
    const response = await api.get('/users/me');
    return response.data;
  }
};

export const usersAPI = {
  list: () => api.get('/users'),
  getManagers: () => api.get('/users/managers/list'),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
};

export const projectsAPI = {
  list: () => api.get('/projects'),
  create: (data) => api.post('/projects', data),
  getMembers: (id) => api.get(`/projects/${id}/members`),
};

export const timeEntriesAPI = {
  list: (params) => api.get('/time-entries', { params }),
  create: (data) => api.post('/time-entries', data),
  getPendingApprovals: () => api.get('/time-entries/pending/approvals'),
  approve: (id, data) => api.post(`/time-entries/${id}/approve`, data),
  reject: (id, data) => api.post(`/time-entries/${id}/reject`, data),
};

export const reportsAPI = {
  getSummary: (params) => api.get('/reports/summary', { params }),
  getByReportingArea: (params) => api.get('/reports/by-area', { params }),
};

export default api;