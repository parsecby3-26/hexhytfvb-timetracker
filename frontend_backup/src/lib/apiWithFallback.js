// API wrapper with fallback to Supabase
import api from './api';
import supabaseService from '../lib/supabase';

const ENABLE_SUPABASE_FALLBACK = process.env.REACT_APP_ENABLE_SUPABASE_FALLBACK === 'true';
const API_TIMEOUT = 5000; // 5 seconds timeout before trying Supabase

// Helper to add timeout to promises
const withTimeout = (promise, timeoutMs) => {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), timeoutMs)
    )
  ]);
};

// Fallback API wrapper
export const apiWithFallback = {
  // Time Entries
  async getTimeEntries(filters) {
    if (!ENABLE_SUPABASE_FALLBACK) {
      return api.get('/time-entries', { params: filters });
    }

    try {
      // Try backend first with timeout
      return await withTimeout(
        api.get('/time-entries', { params: filters }),
        API_TIMEOUT
      );
    } catch (error) {
      console.warn('Backend timeout/error, trying Supabase:', error.message);
      try {
        const data = await supabaseService.getTimeEntries(filters);
        return { data: { data: { entries: data } } };
      } catch (supabaseError) {
        console.error('Supabase fallback failed:', supabaseError);
        throw error;
      }
    }
  },

  async createTimeEntry(data) {
    if (!ENABLE_SUPABASE_FALLBACK) {
      return api.post('/time-entries', data);
    }

    try {
      return await withTimeout(
        api.post('/time-entries', data),
        API_TIMEOUT
      );
    } catch (error) {
      console.warn('Backend timeout/error, trying Supabase:', error.message);
      try {
        const entry = await supabaseService.createTimeEntry(data);
        return { data: { data: entry } };
      } catch (supabaseError) {
        console.error('Supabase fallback failed:', supabaseError);
        throw error;
      }
    }
  },

  // Projects
  async getProjects(filters) {
    if (!ENABLE_SUPABASE_FALLBACK) {
      return api.get('/projects', { params: filters });
    }

    try {
      return await withTimeout(
        api.get('/projects', { params: filters }),
        API_TIMEOUT
      );
    } catch (error) {
      console.warn('Backend timeout/error, trying Supabase:', error.message);
      try {
        const data = await supabaseService.getProjects();
        return { data: { data: { projects: data } } };
      } catch (supabaseError) {
        console.error('Supabase fallback failed:', supabaseError);
        throw error;
      }
    }
  },

  // Users
  async getUsers(filters) {
    if (!ENABLE_SUPABASE_FALLBACK) {
      return api.get('/users', { params: filters });
    }

    try {
      return await withTimeout(
        api.get('/users', { params: filters }),
        API_TIMEOUT
      );
    } catch (error) {
      console.warn('Backend timeout/error, trying Supabase:', error.message);
      try {
        const data = await supabaseService.getUsers();
        return { data: { data: data } };
      } catch (supabaseError) {
        console.error('Supabase fallback failed:', supabaseError);
        throw error;
      }
    }
  },

  // Reports
  async getReports(filters) {
    if (!ENABLE_SUPABASE_FALLBACK) {
      return api.get('/reports/summary', { params: filters });
    }

    try {
      return await withTimeout(
        api.get('/reports/summary', { params: filters }),
        API_TIMEOUT
      );
    } catch (error) {
      console.warn('Backend timeout/error, trying Supabase:', error.message);
      try {
        const data = await supabaseService.getReports(filters);
        // Transform to match API response format
        return { data: { data: { entries: data } } };
      } catch (supabaseError) {
        console.error('Supabase fallback failed:', supabaseError);
        throw error;
      }
    }
  },
};

export default apiWithFallback;
