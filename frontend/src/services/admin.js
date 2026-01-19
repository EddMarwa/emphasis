import apiClient from './api';

// Admin endpoints
export const adminAPI = {
  // Get admin stats
  getStats: async () => {
    const response = await apiClient.get('/admin/stats/');
    return response.data;
  },

  // Get all users
  getUsers: async (page = 1, limit = 20, search = '') => {
    const response = await apiClient.get('/admin/users/', {
      params: { page, limit, search },
    });
    return response.data;
  },

  // Get user details
  getUserDetails: async (userId) => {
    const response = await apiClient.get(`/admin/users/${userId}/`);
    return response.data;
  },

  // Update user status
  updateUserStatus: async (userId, status) => {
    const response = await apiClient.patch(`/admin/users/${userId}/`, {
      account_status: status,
    });
    return response.data;
  },

  // Bot control
  getBotStatus: async () => {
    const response = await apiClient.get('/admin/bot/status/');
    return response.data;
  },

  startBot: async () => {
    const response = await apiClient.post('/admin/bot/start/');
    return response.data;
  },

  stopBot: async () => {
    const response = await apiClient.post('/admin/bot/stop/');
    return response.data;
  },

  // Pending withdrawals
  getPendingWithdrawals: async () => {
    const response = await apiClient.get('/admin/withdrawals/pending/');
    return response.data;
  },

  approveWithdrawal: async (withdrawalId) => {
    const response = await apiClient.post(`/admin/withdrawals/${withdrawalId}/approve/`);
    return response.data;
  },

  rejectWithdrawal: async (withdrawalId) => {
    const response = await apiClient.post(`/admin/withdrawals/${withdrawalId}/reject/`);
    return response.data;
  },

  // Pending KYC
  getPendingKYC: async () => {
    const response = await apiClient.get('/admin/kyc/pending/');
    return response.data;
  },

  approveKYC: async (kycId) => {
    const response = await apiClient.post(`/admin/kyc/${kycId}/approve/`);
    return response.data;
  },

  rejectKYC: async (kycId) => {
    const response = await apiClient.post(`/admin/kyc/${kycId}/reject/`);
    return response.data;
  },
};

