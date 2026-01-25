import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useFetch } from '../hooks/useFetch';
import { apiClient } from '../services/api';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [withdrawals, setWithdrawals] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch dashboard statistics
  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/admin/dashboard/statistics/');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/admin/users/list_users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchWithdrawals = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/admin/withdrawals/pending_withdrawals/');
      setWithdrawals(response.data);
    } catch (error) {
      console.error('Error fetching withdrawals:', error);
    } finally {
      setLoading(false);
    }
  };

  const suspendUser = async (userId, reason) => {
    try {
      await apiClient.post('/api/admin/users/suspend_user/', {
        user_id: userId,
        reason: reason || 'Suspended by admin'
      });
      await fetchUsers();
      alert('User suspended successfully');
    } catch (error) {
      console.error('Error suspending user:', error);
      alert('Failed to suspend user');
    }
  };

  const activateUser = async (userId) => {
    try {
      await apiClient.post('/api/admin/users/activate_user/', {
        user_id: userId
      });
      await fetchUsers();
      alert('User activated successfully');
    } catch (error) {
      console.error('Error activating user:', error);
      alert('Failed to activate user');
    }
  };

  const approveWithdrawal = async (withdrawalId) => {
    try {
      await apiClient.post('/api/admin/withdrawals/approve_withdrawal/', {
        withdrawal_id: withdrawalId
      });
      await fetchWithdrawals();
      alert('Withdrawal approved');
    } catch (error) {
      console.error('Error approving withdrawal:', error);
      alert('Failed to approve withdrawal');
    }
  };

  const rejectWithdrawal = async (withdrawalId, reason) => {
    try {
      await apiClient.post('/api/admin/withdrawals/reject_withdrawal/', {
        withdrawal_id: withdrawalId,
        reason: reason || 'Rejected by admin'
      });
      await fetchWithdrawals();
      alert('Withdrawal rejected');
    } catch (error) {
      console.error('Error rejecting withdrawal:', error);
      alert('Failed to reject withdrawal');
    }
  };

  const generateMonthlyReport = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/admin/reports/monthly_summary/');
      setReportData(response.data);
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const exportUsersCSV = async () => {
    try {
      const response = await apiClient.get('/api/admin/reports/export_users_csv/', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'users_export.csv');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error('Error exporting CSV:', error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(value);
  };

  // Prepare chart data
  const chartColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
  const pieData = stats ? [
    { name: 'Deposited', value: parseFloat(stats.total_deposited) },
    { name: 'Withdrawn', value: parseFloat(stats.total_withdrawn) },
    { name: 'Profit', value: parseFloat(stats.total_profit) },
  ] : [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-600 mt-1">Platform management and reporting</p>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex space-x-4 mb-8 border-b border-gray-200">
          <button
            onClick={() => { setActiveTab('overview'); fetchStats(); }}
            className={`px-4 py-2 font-medium ${activeTab === 'overview' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Overview
          </button>
          <button
            onClick={() => { setActiveTab('users'); fetchUsers(); }}
            className={`px-4 py-2 font-medium ${activeTab === 'users' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Users
          </button>
          <button
            onClick={() => { setActiveTab('withdrawals'); fetchWithdrawals(); }}
            className={`px-4 py-2 font-medium ${activeTab === 'withdrawals' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Withdrawals
          </button>
          <button
            onClick={() => { setActiveTab('reports'); generateMonthlyReport(); }}
            className={`px-4 py-2 font-medium ${activeTab === 'reports' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Reports
          </button>
        </div>

        {loading && <div className="text-center py-8"><p className="text-gray-600">Loading...</p></div>}

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="space-y-8">
            {/* Statistics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title="Total Users"
                value={stats.total_users}
                icon="👥"
              />
              <StatCard
                title="Active Users"
                value={stats.active_users}
                icon="✅"
              />
              <StatCard
                title="Assets Under Management"
                value={formatCurrency(stats.assets_under_management)}
                icon="💰"
              />
              <StatCard
                title="Total Profit"
                value={formatCurrency(stats.total_profit)}
                icon="📈"
              />
            </div>

            {/* Financial Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Summary</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Deposited:</span>
                    <span className="font-semibold">{formatCurrency(stats.total_deposited)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Withdrawn:</span>
                    <span className="font-semibold">{formatCurrency(stats.total_withdrawn)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Profit:</span>
                    <span className="font-semibold text-green-600">{formatCurrency(stats.total_profit)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Platform Fees (10%):</span>
                    <span className="font-semibold text-blue-600">{formatCurrency(stats.total_fees)}</span>
                  </div>
                  <div className="border-t pt-4 flex justify-between">
                    <span className="text-gray-600">Pending Withdrawals:</span>
                    <span className="font-semibold">{stats.pending_withdrawals}</span>
                  </div>
                </div>
              </div>

              {/* Fund Allocation Pie Chart */}
              {pieData.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Fund Allocation</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* System Status */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatusIndicator label="Deposits" status="active" />
                <StatusIndicator label="Withdrawals" status="active" />
                <StatusIndicator label="M-Pesa" status="configured" />
                <StatusIndicator label="Crypto" status="configured" />
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">User Management</h3>
                <button
                  onClick={exportUsersCSV}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Export CSV
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">User ID</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Email</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Balance</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Joined</th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm text-gray-900 font-medium">{user.user_id}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            user.account_status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {user.account_status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm font-semibold text-gray-900">{formatCurrency(user.balance)}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{new Date(user.created_at).toLocaleDateString()}</td>
                        <td className="px-6 py-4 text-sm space-x-2">
                          <button
                            onClick={() => setSelectedUser(user)}
                            className="text-blue-600 hover:text-blue-800 font-medium"
                          >
                            View
                          </button>
                          {user.account_status === 'active' ? (
                            <button
                              onClick={() => suspendUser(user.user_id)}
                              className="text-red-600 hover:text-red-800 font-medium"
                            >
                              Suspend
                            </button>
                          ) : (
                            <button
                              onClick={() => activateUser(user.user_id)}
                              className="text-green-600 hover:text-green-800 font-medium"
                            >
                              Activate
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* User Details Modal */}
            {selectedUser && (
              <UserDetailsModal
                user={selectedUser}
                onClose={() => setSelectedUser(null)}
                formatCurrency={formatCurrency}
              />
            )}
          </div>
        )}

        {/* Withdrawals Tab */}
        {activeTab === 'withdrawals' && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Pending Withdrawals</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">User ID</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Amount</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Method</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Requested</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {withdrawals.map((withdrawal) => (
                    <tr key={withdrawal.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{withdrawal.user_id}</td>
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900">{formatCurrency(withdrawal.amount)}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{withdrawal.payment_method}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800">
                          {withdrawal.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">{new Date(withdrawal.created_at).toLocaleDateString()}</td>
                      <td className="px-6 py-4 text-sm space-x-2">
                        <button
                          onClick={() => approveWithdrawal(withdrawal.id)}
                          className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-xs font-medium"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => rejectWithdrawal(withdrawal.id)}
                          className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-xs font-medium"
                        >
                          Reject
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && reportData && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <ReportCard
                title="Total Deposits"
                value={formatCurrency(reportData.total_deposits)}
                color="blue"
              />
              <ReportCard
                title="Total Withdrawals"
                value={formatCurrency(reportData.total_withdrawals)}
                color="red"
              />
              <ReportCard
                title="Total Profits"
                value={formatCurrency(reportData.total_profits)}
                color="green"
              />
              <ReportCard
                title="Platform Revenue (Fees)"
                value={formatCurrency(reportData.total_fees)}
                color="purple"
              />
              <ReportCard
                title="New Users"
                value={reportData.new_users_count}
                color="indigo"
              />
              <ReportCard
                title="AUM"
                value={formatCurrency(reportData.assets_under_management)}
                color="yellow"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper Components
const StatCard = ({ title, value, icon }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-600 text-sm font-medium">{title}</p>
        <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </div>
);

const StatusIndicator = ({ label, status }) => (
  <div className="flex items-center space-x-3">
    <div className={`w-3 h-3 rounded-full ${
      status === 'active' ? 'bg-green-600' : 'bg-yellow-600'
    }`}></div>
    <span className="text-sm text-gray-700">{label}</span>
  </div>
);

const ReportCard = ({ title, value, color }) => {
  const colorClasses = {
    blue: 'bg-blue-50 border-l-4 border-blue-600',
    red: 'bg-red-50 border-l-4 border-red-600',
    green: 'bg-green-50 border-l-4 border-green-600',
    purple: 'bg-purple-50 border-l-4 border-purple-600',
    indigo: 'bg-indigo-50 border-l-4 border-indigo-600',
    yellow: 'bg-yellow-50 border-l-4 border-yellow-600',
  };

  return (
    <div className={`rounded-lg p-6 ${colorClasses[color]}`}>
      <p className="text-gray-600 text-sm font-medium">{title}</p>
      <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
    </div>
  );
};

const UserDetailsModal = ({ user, onClose, formatCurrency }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">User Details</h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 font-bold text-xl"
        >
          ✕
        </button>
      </div>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">User ID</p>
            <p className="text-lg font-semibold text-gray-900">{user.user_id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Email</p>
            <p className="text-lg font-semibold text-gray-900">{user.email}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Status</p>
            <p className="text-lg font-semibold text-gray-900">{user.account_status}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Joined</p>
            <p className="text-lg font-semibold text-gray-900">{new Date(user.created_at).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Current Balance</p>
            <p className="text-lg font-semibold text-gray-900">{formatCurrency(user.balance)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Deposited</p>
            <p className="text-lg font-semibold text-gray-900">{formatCurrency(user.total_deposited)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Profit</p>
            <p className="text-lg font-semibold text-green-600">{formatCurrency(user.total_profit)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Active Investments</p>
            <p className="text-lg font-semibold text-gray-900">{user.investment_count}</p>
          </div>
        </div>
      </div>
      <button
        onClick={onClose}
        className="mt-6 w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium"
      >
        Close
      </button>
    </div>
  </div>
);

export default AdminDashboard;
