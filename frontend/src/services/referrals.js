import apiClient from './api';

// Referrals endpoints
export const referralsAPI = {
  // Get referral stats
  getStats: async () => {
    const response = await apiClient.get('/referrals/stats/');
    return response.data;
  },

  // Get referral code
  getReferralCode: async () => {
    const response = await apiClient.get('/referrals/code/');
    return response.data;
  },

  // Get my referrals
  getMyReferrals: async () => {
    const response = await apiClient.get('/referrals/my-referrals/');
    return response.data;
  },

  // Get referral analytics
  getAnalytics: async (period = '30d') => {
    const response = await apiClient.get('/referrals/analytics/', {
      params: { period },
    });
    return response.data;
  },

  // Get leaderboard
  getLeaderboard: async (limit = 10) => {
    const response = await apiClient.get('/referrals/leaderboard/', {
      params: { limit },
    });
    return response.data;
  },
};

