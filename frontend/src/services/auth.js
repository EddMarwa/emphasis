import apiClient from './api';

// Authentication endpoints
export const authAPI = {
  // Login (accepts email or user_id)
  login: async (emailOrUserId, password) => {
    const response = await apiClient.post('/auth/login/', {
      email_or_user_id: emailOrUserId, // Backend should handle both
      password,
    });
    return response.data;
  },

  // Register
  register: async (userData) => {
    const response = await apiClient.post('/auth/register/', userData);
    return response.data;
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/user/');
    return response.data;
  },

  // Refresh token
  refreshToken: async (refreshToken) => {
    const response = await apiClient.post('/auth/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },

  // Logout
  logout: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await apiClient.post('/auth/logout/', {
          refresh: refreshToken,
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  // Forgot password
  forgotPassword: async (email) => {
    const response = await apiClient.post('/auth/forgot-password/', {
      email,
    });
    return response.data;
  },

  // Reset password
  resetPassword: async (token, newPassword) => {
    const response = await apiClient.post('/auth/reset-password/', {
      token,
      password: newPassword,
    });
    return response.data;
  },
};

