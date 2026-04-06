// Direct Supabase connection (fallback when backend is down)
// NOTE: This requires @supabase/supabase-js client library
// Install with: npm install @supabase/supabase-js

const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY;

let supabase = null;

// Lazy load Supabase client only when needed
const getSupabaseClient = async () => {
  if (supabase) return supabase;
  
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    console.warn('Supabase credentials not configured');
    return null;
  }

  try {
    const { createClient } = await import('@supabase/supabase-js');
    supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    return supabase;
  } catch (error) {
    console.error('Failed to initialize Supabase client:', error);
    return null;
  }
};

export const supabaseService = {
  // Get the authenticated Supabase client
  async getClient() {
    return getSupabaseClient();
  },

  // Get current user session
  async getSession() {
    const client = await getSupabaseClient();
    if (!client) return null;
    
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    return { token };
  },

  // Query time entries
  async getTimeEntries(filters) {
    const client = await getSupabaseClient();
    if (!client) throw new Error('Supabase client not available');

    const token = localStorage.getItem('token');
    if (!token) throw new Error('Not authenticated');

    let query = client
      .from('time_entries')
      .select('*');

    if (filters?.start_date) {
      query = query.gte('work_date', filters.start_date);
    }
    if (filters?.end_date) {
      query = query.lte('work_date', filters.end_date);
    }
    if (filters?.user_id) {
      query = query.eq('user_id', filters.user_id);
    }

    const { data, error } = await query;
    if (error) throw error;
    return data;
  },

  // Create time entry
  async createTimeEntry(data) {
    const client = await getSupabaseClient();
    if (!client) throw new Error('Supabase client not available');

    const token = localStorage.getItem('token');
    if (!token) throw new Error('Not authenticated');

    const { data: entry, error } = await client
      .from('time_entries')
      .insert([{ ...data, status: 'PENDING' }])
      .select();

    if (error) throw error;
    return entry;
  },

  // Get projects
  async getProjects() {
    const client = await getSupabaseClient();
    if (!client) throw new Error('Supabase client not available');

    const token = localStorage.getItem('token');
    if (!token) throw new Error('Not authenticated');

    const { data, error } = await client
      .from('projects')
      .select('*');

    if (error) throw error;
    return data;
  },

  // Get users
  async getUsers() {
    const client = await getSupabaseClient();
    if (!client) throw new Error('Supabase client not available');

    const token = localStorage.getItem('token');
    if (!token) throw new Error('Not authenticated');

    const { data, error } = await client
      .from('users')
      .select('*');

    if (error) throw error;
    return data;
  },

  // Get reports
  async getReports(filters) {
    const client = await getSupabaseClient();
    if (!client) throw new Error('Supabase client not available');

    const token = localStorage.getItem('token');
    if (!token) throw new Error('Not authenticated');

    let query = client
      .from('time_entries')
      .select('*')
      .eq('status', 'APPROVED');

    if (filters?.start_date) {
      query = query.gte('work_date', filters.start_date);
    }
    if (filters?.end_date) {
      query = query.lte('work_date', filters.end_date);
    }

    const { data, error } = await query;
    if (error) throw error;
    return data;
  },
};

export default supabaseService;
