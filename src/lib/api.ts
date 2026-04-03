const API_BASE = "https://timetracker-api-m8k7.onrender.com/api";

// ... (request function stays the same)

export const authApi = {
  login: async (email: string, password: string) => {
    // Note: Adjusted path to match your Swagger's /api/auth/auth/login
    const result = await api.post<any>('/auth/auth/login', { email, password });
    
    // Adjusted to match the actual JSON keys: "data", "profile", "token"
    return {
      profile: {
        id: result.data.profile.id,
        name: result.data.profile.name,
        email: result.data.profile.email,
        roles: result.data.profile.roles // already in correct format from your Swagger screenshot
      },
      token: result.data.token
    };
  },
  me: async () => {
    // Adjusted to match /api/users/users/me from your successful test
    const response = await api.get<any>('/users/users/me');
    return response.data; 
  }
};