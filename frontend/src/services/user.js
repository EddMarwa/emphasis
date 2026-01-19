import apiClient from './api';

// User endpoints
export const userAPI = {
  // Get user profile
  getProfile: async () => {
    const response = await apiClient.get('/users/profile/');
    return response.data;
  },

  // Update user profile
  updateProfile: async (data) => {
    const response = await apiClient.patch('/users/profile/', data);
    return response.data;
  },

  // Change password
  changePassword: async (oldPassword, newPassword) => {
    const response = await apiClient.post('/users/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: newPassword,  // Backend expects this
    });
    return response.data;
  },
};

