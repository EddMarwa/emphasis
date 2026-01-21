import apiClient from './api';

// Investment endpoints
export const investmentAPI = {
  getInvestments: async () => {
    const response = await apiClient.get('/investments/');
    return response.data;
  },

  getInvestment: async (investmentId) => {
    const response = await apiClient.get(`/investments/${investmentId}/`);
    return response.data;
  },

  createInvestment: async (data) => {
    const response = await apiClient.post('/investments/', data);
    return response.data;
  },

  updateInvestment: async (investmentId, data) => {
    const response = await apiClient.patch(`/investments/${investmentId}/`, data);
    return response.data;
  },

  getAllocations: async (investmentId) => {
    const response = await apiClient.get(`/investments/${investmentId}/allocations/`);
    return response.data;
  },
};

// Payment endpoints
export const paymentAPI = {
  // Balance
  getBalance: async () => {
    const response = await apiClient.get('/balance/');
    return response.data;
  },

  // Deposits
  getDeposits: async () => {
    const response = await apiClient.get('/deposits/');
    return response.data;
  },

  getDeposit: async (depositId) => {
    const response = await apiClient.get(`/deposits/${depositId}/`);
    return response.data;
  },

  createDeposit: async (data) => {
    const response = await apiClient.post('/deposits/', data);
    return response.data;
  },

  // Withdrawals
  getWithdrawals: async () => {
    const response = await apiClient.get('/withdrawals/');
    return response.data;
  },

  getWithdrawal: async (withdrawalId) => {
    const response = await apiClient.get(`/withdrawals/${withdrawalId}/`);
    return response.data;
  },

  createWithdrawal: async (data) => {
    const response = await apiClient.post('/withdrawals/', data);
    return response.data;
  },

  // Transactions
  getTransactions: async (params = {}) => {
    const response = await apiClient.get('/transactions/', { params });
    return response.data;
  },

  exportTransactions: async (params = {}) => {
    const response = await apiClient.get('/transactions/export/', { 
      params,
      responseType: 'blob'
    });
    return response.data;
  },
};
