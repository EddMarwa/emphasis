import React, { useState, useEffect } from 'react';
import { Wallet, TrendingUp, Bot, DollarSign, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import Layout from '../components/layout/Layout';
import StatCard from '../components/dashboard/StatCard';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { dashboardAPI } from '../services/dashboard';
import { useToast } from '../contexts/ToastContext';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
        <p className="text-sm font-semibold text-text-dark">{payload[0].payload.date}</p>
        <p className="text-lg font-bold text-electric-blue">
          KES {payload[0].value.toLocaleString()}
        </p>
      </div>
    );
  }
  return null;
};

const Dashboard = ({ user, onLogout }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total_balance: 0,
    total_profit: 0,
    bot_performance: 0,
    platform_fee: 0,
  });
  const [performanceData, setPerformanceData] = useState([]);
  const [fundAllocationData, setFundAllocationData] = useState([]);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const { error: showError } = useToast();
  
  useEffect(() => {
    loadDashboardData();
  }, [selectedPeriod]);
  
  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load stats
      const statsData = await dashboardAPI.getStats();
      setStats(statsData);
      
      // Load performance data
      const perfData = await dashboardAPI.getPerformance(selectedPeriod);
      setPerformanceData(perfData.data || []);
      
      // Load fund allocation
      const allocationData = await dashboardAPI.getFundAllocation();
      setFundAllocationData(allocationData.data || []);
      
      // Load recent transactions
      const transactionsData = await dashboardAPI.getRecentTransactions(5);
      const transactions = (transactionsData.transactions || []).map(t => ({
        ...t,
        icon: t.type === 'Deposit' ? ArrowDownRight : ArrowUpRight,
      }));
      setRecentTransactions(transactions);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      showError('Failed to load dashboard data');
      // Use empty/default data on error
      setPerformanceData([]);
      setFundAllocationData([
        { name: 'Active Trading', value: 75, color: '#00D9FF' },
        { name: 'Reserved', value: 25, color: '#14B8A6' },
      ]);
      setRecentTransactions([]);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-8 animate-fade-in">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Dashboard</h1>
          <p className="text-text-gray">Welcome back, {user?.username || 'User'}! Here's your investment overview.</p>
        </div>
        
        {/* Stats Cards Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded-xl animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Balance"
              value={`KES ${stats.total_balance?.toLocaleString() || '0'}`}
              change="+12.5%"
              changeType="positive"
              icon={Wallet}
              iconColor="bg-gradient-button-primary"
            />
            <StatCard
              title="Total Profit"
              value={`KES ${stats.total_profit?.toLocaleString() || '0'}`}
              change="+31.2%"
              changeType="positive"
              icon={TrendingUp}
              iconColor="bg-gradient-success"
            />
            <StatCard
              title="Bot Performance"
              value={`${stats.bot_performance || 0}%`}
              change="Win Rate"
              changeType="positive"
              icon={Bot}
              iconColor="bg-gradient-to-r from-purple-500 to-pink-500"
            />
            <StatCard
              title="Platform Fee"
              value={`KES ${stats.platform_fee?.toLocaleString() || '0'}`}
              change="10%"
              changeType="neutral"
              icon={DollarSign}
              iconColor="bg-gradient-to-r from-orange-500 to-yellow-500"
            />
          </div>
        )}
        
        {/* Performance Chart */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-text-dark mb-1">Performance Overview</h2>
              <p className="text-sm text-text-gray">Last 7 days performance</p>
            </div>
            <div className="flex gap-2">
              {['7d', '30d', '90d', '1y'].map((period) => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                    selectedPeriod === period
                      ? 'bg-gradient-button-primary text-white shadow-lg'
                      : 'bg-gray-100 text-text-gray hover:bg-gray-200'
                  }`}
                >
                  {period.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={performanceData.length > 0 ? performanceData : [{ date: 'No Data', value: 0 }]}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00D9FF" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#1E40AF" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="date" 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => `KES ${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#00D9FF"
                strokeWidth={3}
                fill="url(#colorValue)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
        
        {/* Fund Allocation & Recent Transactions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Fund Allocation */}
          <Card className="p-6">
            <h2 className="text-xl font-bold text-text-dark mb-6">Fund Allocation</h2>
            <div className="flex items-center justify-center">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={fundAllocationData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {fundAllocationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => `${value}%`}
                    contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB' }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    formatter={(value, entry) => (
                      <span style={{ color: entry.color, fontWeight: 500 }}>
                        {value}: {entry.payload.value}%
                      </span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
          
          {/* Recent Transactions */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-text-dark">Recent Transactions</h2>
              <button className="text-sm font-medium text-electric-blue hover:text-electric-cyan transition-colors">
                View All
              </button>
            </div>
            
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-8 text-text-gray">Loading transactions...</div>
              ) : recentTransactions.length === 0 ? (
                <div className="text-center py-8 text-text-gray">No transactions yet</div>
              ) : (
                recentTransactions.map((transaction) => {
                  const Icon = transaction.icon;
                  const isPositive = transaction.type === 'Profit' || transaction.type === 'Deposit';
                
                return (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        isPositive ? 'bg-emerald-100' : 'bg-blue-100'
                      }`}>
                        <Icon
                          size={20}
                          className={isPositive ? 'text-emerald-600' : 'text-blue-600'}
                        />
                      </div>
                      <div>
                        <p className="font-semibold text-text-dark">{transaction.type}</p>
                        <p className="text-sm text-text-gray">{transaction.method}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        isPositive ? 'text-emerald-600' : 'text-blue-600'
                      }`}>
                        {isPositive ? '+' : '-'}KES {transaction.amount.toLocaleString()}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="text-xs text-text-gray">{transaction.date}</p>
                        <Badge
                          variant={transaction.status === 'completed' ? 'success' : 'warning'}
                          size="sm"
                        >
                          {transaction.status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                );
                })
              )}
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;

