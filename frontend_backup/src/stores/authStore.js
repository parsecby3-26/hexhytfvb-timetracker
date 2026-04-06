import { create } from 'zustand';
import { authAPI } from '../services/api';

const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('user')) || null,
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.login(email, password);
      const { data } = response.data;
      
      if (response.data.status === 'error') {
        set({ loading: false, error: response.data.message });
        return false;
      }
      
      if (response.data.status === 'otp_required') {
        set({ loading: false, error: null });
        return 'otp_required';
      }

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.profile));
      
      set({
        user: data.profile,
        token: data.token,
        isAuthenticated: true,
        loading: false,
        error: null,
      });
      
      return true;
    } catch (error) {
      const message = error.response?.data?.message || 'Login failed';
      set({ loading: false, error: message });
      return false;
    }
  },

  verifyFirstLogin: async (email, otp, newPassword) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.verifyFirstLogin({ email, otp, new_password: newPassword });
      const { data } = response.data;
      
      if (response.data.status === 'error') {
        set({ loading: false, error: response.data.message });
        return false;
      }

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.profile));
      
      set({
        user: data.profile,
        token: data.token,
        isAuthenticated: true,
        loading: false,
        error: null,
      });
      
      return true;
    } catch (error) {
      const message = error.response?.data?.message || 'Verification failed';
      set({ loading: false, error: message });
      return false;
    }
  },

  register: async (userData) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.register(userData);
      
      if (response.data.status === 'error') {
        set({ loading: false, error: response.data.message });
        return false;
      }

      set({ loading: false });
      return true;
    } catch (error) {
      const message = error.response?.data?.message || 'Registration failed';
      set({ loading: false, error: message });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    });
  },

  fetchCurrentUser: async () => {
    try {
      const response = await authAPI.getCurrentUser();
      const user = response.data.data;
      localStorage.setItem('user', JSON.stringify(user));
      set({ user });
    } catch (error) {
      console.error('Failed to fetch current user:', error);
    }
  },

  hasRole: (roleName) => {
    const user = get().user;
    if (!user || !user.roles) return false;
    return user.roles.some(role => role.value === roleName);
  },

  isAdmin: () => get().hasRole('Admin'),
  isManager: () => get().hasRole('Manager'),
  isMember: () => get().hasRole('Member'),

  clearError: () => set({ error: null }),
}));

export default useAuthStore;



