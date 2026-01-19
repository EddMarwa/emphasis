import apiClient from './api';

// Funds/Transactions endpoints
export const fundsAPI = {
  // Deposit
  deposit: async (amount, method) => {
    const response = await apiClient.post('/funds/deposit/', {
      amount,
      payment_method: method,
    });
    return response.data;
  },

  // Withdraw
  withdraw: async (amount, method) => {
    const response = await apiClient.post('/funds/withdraw/', {
      amount,
      payment_method: method,
    });
    return response.data;
  },

  // Get transaction history
  getTransactions: async (page = 1, limit = 20) => {
    const response = await apiClient.get('/funds/transactions/', {
      params: { page, limit },
    });
    return response.data;
  },

  // Get balance
  getBalance: async () => {
    const response = await apiClient.get('/funds/balance/');
    return response.data;
  },
};

