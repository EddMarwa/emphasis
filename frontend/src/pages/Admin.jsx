import React, { useState } from 'react';
import { Users, DollarSign, TrendingUp, Power, Search, MoreVertical, CheckCircle2, XCircle, Clock } from 'lucide-react';
import Layout from '../components/layout/Layout';
import StatCard from '../components/dashboard/StatCard';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Input from '../components/common/Input';
import Modal from '../components/common/Modal';
import { useToast } from '../contexts/ToastContext';

const adminStats = [
  { id: 1, title: 'Total Users', value: '1,247', change: '+23 this week', changeType: 'positive', icon: Users },
  { id: 2, title: 'Total AUM', value: 'KES 52.4M', change: '+8.2%', changeType: 'positive', icon: DollarSign },
  { id: 3, title: 'Platform Revenue', value: 'KES 5.24M', change: '+12.5%', changeType: 'positive', icon: TrendingUp },
];

const recentUsers = [
  { id: 1, userId: 'KE-QC-01247', name: 'John Doe', email: 'john@example.com', balance: 125000, status: 'active', joinedDate: '2024-01-15' },
  { id: 2, userId: 'KE-QC-01246', name: 'Jane Smith', email: 'jane@example.com', balance: 85000, status: 'active', joinedDate: '2024-01-14' },
  { id: 3, userId: 'KE-QC-01245', name: 'Mike Johnson', email: 'mike@example.com', balance: 200000, status: 'pending', joinedDate: '2024-01-14' },
  { id: 4, userId: 'KE-QC-01244', name: 'Sarah Williams', email: 'sarah@example.com', balance: 50000, status: 'active', joinedDate: '2024-01-13' },
  { id: 5, userId: 'KE-QC-01243', name: 'David Brown', email: 'david@example.com', balance: 300000, status: 'suspended', joinedDate: '2024-01-12' },
];

const pendingWithdrawals = [
  { id: 1, userId: 'KE-QC-01247', amount: 50000, method: 'M-Pesa', date: '2024-01-15', status: 'pending' },
  { id: 2, userId: 'KE-QC-01245', amount: 100000, method: 'USDT TRC20', date: '2024-01-14', status: 'pending' },
  { id: 3, userId: 'KE-QC-01244', amount: 25000, method: 'M-Pesa', date: '2024-01-14', status: 'pending' },
];

const pendingKYC = [
  { id: 1, userId: 'KE-QC-01245', name: 'Mike Johnson', submittedDate: '2024-01-14', status: 'pending' },
  { id: 2, userId: 'KE-QC-01240', name: 'Emily Davis', submittedDate: '2024-01-13', status: 'pending' },
];

const Admin = ({ user, onLogout }) => {
  const [botStatus, setBotStatus] = useState('active');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const { success, error: showError } = useToast();
  
  const handleBotToggle = () => {
    const newStatus = botStatus === 'active' ? 'inactive' : 'active';
    setBotStatus(newStatus);
    success(`Trading bot ${newStatus === 'active' ? 'started' : 'stopped'} successfully`);
  };
  
  const handleAction = (action, item, type) => {
    if (action === 'approve') {
      success(`${type} approved successfully`);
    } else if (action === 'reject') {
      showError(`${type} rejected`);
    }
  };
  
  const filteredUsers = recentUsers.filter(user =>
    user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.userId.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-8 animate-fade-in">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Admin Dashboard</h1>
          <p className="text-text-gray">Manage platform operations and monitor activity</p>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {adminStats.map((stat) => {
            const Icon = stat.icon;
            return (
              <StatCard
                key={stat.id}
                title={stat.title}
                value={stat.value}
                change={stat.change}
                changeType={stat.changeType}
                icon={Icon}
                iconColor="bg-gradient-button-primary"
              />
            );
          })}
        </div>
        
        {/* Bot Control Panel */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-text-dark mb-2">Trading Bot Control</h2>
              <p className="text-text-gray">Start or stop the automated trading bot</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${
                  botStatus === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'
                }`}></div>
                <span className="font-semibold text-text-dark">
                  Status: <span className={botStatus === 'active' ? 'text-emerald-600' : 'text-gray-600'}>
                    {botStatus === 'active' ? 'Active' : 'Inactive'}
                  </span>
                </span>
              </div>
              <Button
                variant={botStatus === 'active' ? 'danger' : 'success'}
                onClick={handleBotToggle}
                className="flex items-center gap-2"
              >
                <Power size={18} />
                {botStatus === 'active' ? 'Stop Bot' : 'Start Bot'}
              </Button>
            </div>
          </div>
        </Card>
        
        {/* Recent Users Table */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-text-dark">Recent Users</h2>
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-gray" />
                <Input
                  type="text"
                  placeholder="Search users..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">User ID</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Name</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Email</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Balance</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Status</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-mono text-sm font-semibold text-text-dark">{user.userId}</span>
                    </td>
                    <td className="py-3 px-4 font-medium text-text-dark">{user.name}</td>
                    <td className="py-3 px-4 text-text-gray text-sm">{user.email}</td>
                    <td className="py-3 px-4 font-semibold text-text-dark">KES {user.balance.toLocaleString()}</td>
                    <td className="py-3 px-4">
                      <Badge
                        variant={
                          user.status === 'active' ? 'success' :
                          user.status === 'pending' ? 'warning' :
                          'error'
                        }
                        size="sm"
                      >
                        {user.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => {
                          setSelectedUser(user);
                          setShowUserModal(true);
                        }}
                        className="p-2 text-text-gray hover:text-electric-blue hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        <MoreVertical size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
        
        {/* Pending Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pending Withdrawals */}
          <Card className="p-6">
            <h2 className="text-xl font-bold text-text-dark mb-6">Pending Withdrawals</h2>
            <div className="space-y-4">
              {pendingWithdrawals.map((withdrawal) => (
                <div
                  key={withdrawal.id}
                  className="p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-semibold text-text-dark font-mono text-sm">{withdrawal.userId}</p>
                      <p className="text-sm text-text-gray">{withdrawal.method}</p>
                    </div>
                    <Badge variant="warning" size="sm">
                      <Clock size={12} className="mr-1" />
                      Pending
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-lg font-bold text-text-dark">KES {withdrawal.amount.toLocaleString()}</p>
                      <p className="text-xs text-text-gray">{withdrawal.date}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleAction('approve', withdrawal, 'Withdrawal')}
                        className="p-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
                      >
                        <CheckCircle2 size={18} />
                      </button>
                      <button
                        onClick={() => handleAction('reject', withdrawal, 'Withdrawal')}
                        className="p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                      >
                        <XCircle size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
          
          {/* Pending KYC Verifications */}
          <Card className="p-6">
            <h2 className="text-xl font-bold text-text-dark mb-6">Pending KYC Verifications</h2>
            <div className="space-y-4">
              {pendingKYC.map((kyc) => (
                <div
                  key={kyc.id}
                  className="p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-semibold text-text-dark">{kyc.name}</p>
                      <p className="text-sm text-text-gray font-mono">{kyc.userId}</p>
                    </div>
                    <Badge variant="warning" size="sm">
                      <Clock size={12} className="mr-1" />
                      Pending
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-text-gray">Submitted: {kyc.submittedDate}</p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleAction('approve', kyc, 'KYC')}
                        className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors text-sm font-medium"
                      >
                        Review
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
        
        {/* User Detail Modal */}
        {selectedUser && (
          <Modal
            isOpen={showUserModal}
            onClose={() => {
              setShowUserModal(false);
              setSelectedUser(null);
            }}
            title={`User Details - ${selectedUser.name}`}
            size="md"
          >
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-xl">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-text-gray">User ID:</span>
                    <span className="font-semibold font-mono text-text-dark">{selectedUser.userId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-gray">Email:</span>
                    <span className="font-semibold text-text-dark">{selectedUser.email}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-gray">Balance:</span>
                    <span className="font-bold text-text-dark">KES {selectedUser.balance.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-gray">Status:</span>
                    <Badge
                      variant={
                        selectedUser.status === 'active' ? 'success' :
                        selectedUser.status === 'pending' ? 'warning' :
                        'error'
                      }
                    >
                      {selectedUser.status}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-gray">Joined:</span>
                    <span className="font-semibold text-text-dark">{selectedUser.joinedDate}</span>
                  </div>
                </div>
              </div>
              <div className="flex gap-3">
                <Button variant="primary" className="flex-1">View Full Profile</Button>
                <Button variant="secondary" className="flex-1">Transaction History</Button>
              </div>
            </div>
          </Modal>
        )}
      </div>
    </Layout>
  );
};

export default Admin;

