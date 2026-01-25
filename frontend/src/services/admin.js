import apiClient from './api';

// Admin endpoints
export const adminAPI = {
  // Get admin stats
  getStats: async () => {
    const response = await apiClient.get('/admin/dashboard/statistics/');
    return response;
  },

  // Get all users
  getUsers: async (page = 1, limit = 20, search = '') => {
    const response = await apiClient.get('/admin/users/list_users/', {
      params: { page, limit, search },
    });
    return response;
  },

  // Get user details
  getUserDetails: async (userId) => {
    const response = await apiClient.get('/admin/users/user_detail/', {
      params: { pk: userId }
    });
    return response.data;
  },

  // Suspend user
  suspendUser: async (userId, reason) => {
    const response = await apiClient.post('/admin/users/suspend_user/', {
      user_id: userId,
      reason
    });
    return response.data;
  },

  // Activate user
  activateUser: async (userId, reason) => {
    const response = await apiClient.post('/admin/users/activate_user/', {
      user_id: userId,
      reason
    });
    return response.data;
  },

  // Bot control
  getBotStatus: async () => {
    const response = await apiClient.get('/bot/config/my_config/');
    return response.data;
  },

  startBot: async () => {
    const response = await apiClient.post('/bot/config/start_bot/');
    return response.data;
  },

  stopBot: async () => {
    const response = await apiClient.post('/bot/config/stop_bot/');
    return response.data;
  },

  // Pending withdrawals
  getPendingWithdrawals: async () => {
    const response = await apiClient.get('/admin/withdrawals/pending_withdrawals/');
    return response.data;
  },

  approveWithdrawal: async (withdrawalId, reason) => {
    const response = await apiClient.post('/admin/withdrawals/approve_withdrawal/', {
      withdrawal_id: withdrawalId,
      reason
    });
    return response.data;
  },

  rejectWithdrawal: async (withdrawalId, reason) => {
    const response = await apiClient.post('/admin/withdrawals/reject_withdrawal/', {
      withdrawal_id: withdrawalId,
      reason
    });
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

  // Create user (admin initiated)
  createUser: async (payload) => {
    const response = await apiClient.post('/admin/users/create_user/', payload);
    return response.data;
  },
};

