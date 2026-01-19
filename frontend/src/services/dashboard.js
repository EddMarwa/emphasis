import apiClient from './api';

// Dashboard endpoints
export const dashboardAPI = {
  // Get dashboard stats
  getStats: async () => {
    const response = await apiClient.get('/dashboard/stats/');
    return response.data;
  },

  // Get performance data
  getPerformance: async (period = '7d') => {
    const response = await apiClient.get(`/dashboard/performance/`, {
      params: { period },
    });
    return response.data;
  },

  // Get fund allocation
  getFundAllocation: async () => {
    const response = await apiClient.get('/dashboard/fund-allocation/');
    return response.data;
  },

  // Get recent transactions
  getRecentTransactions: async (limit = 5) => {
    const response = await apiClient.get('/dashboard/transactions/', {
      params: { limit },
    });
    return response.data;
  },
};

