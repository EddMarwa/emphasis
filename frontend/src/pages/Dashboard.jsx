import React, { useState } from 'react';
import { Wallet, TrendingUp, Bot, DollarSign, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import Layout from '../components/layout/Layout';
import StatCard from '../components/dashboard/StatCard';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Mock data
const performanceData = [
  { date: 'Mon', value: 25000 },
  { date: 'Tue', value: 28000 },
  { date: 'Wed', value: 32000 },
  { date: 'Thu', value: 29500 },
  { date: 'Fri', value: 35000 },
  { date: 'Sat', value: 38000 },
  { date: 'Sun', value: 42000 },
];

const fundAllocationData = [
  { name: 'Active Trading', value: 75, color: '#00D9FF' },
  { name: 'Reserved', value: 25, color: '#14B8A6' },
];

const recentTransactions = [
  { id: 1, type: 'Deposit', method: 'M-Pesa', amount: 50000, date: '2024-01-15', status: 'completed', icon: ArrowDownRight },
  { id: 2, type: 'Profit', method: 'Trading Bot', amount: 2500, date: '2024-01-14', status: 'completed', icon: ArrowUpRight },
  { id: 3, type: 'Withdrawal', method: 'USDT TRC20', amount: 10000, date: '2024-01-13', status: 'pending', icon: ArrowUpRight },
  { id: 4, type: 'Profit', method: 'Trading Bot', amount: 1800, date: '2024-01-12', status: 'completed', icon: ArrowUpRight },
  { id: 5, type: 'Deposit', method: 'Bitcoin', amount: 75000, date: '2024-01-10', status: 'completed', icon: ArrowDownRight },
];

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
  
  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-8 animate-fade-in">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Dashboard</h1>
          <p className="text-text-gray">Welcome back, {user?.username || 'User'}! Here's your investment overview.</p>
        </div>
        
        {/* Stats Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Balance"
            value="KES 420,000"
            change="+12.5%"
            changeType="positive"
            icon={Wallet}
            iconColor="bg-gradient-button-primary"
          />
          <StatCard
            title="Total Profit"
            value="KES 95,000"
            change="+31.2%"
            changeType="positive"
            icon={TrendingUp}
            iconColor="bg-gradient-success"
          />
          <StatCard
            title="Bot Performance"
            value="87.5%"
            change="Win Rate"
            changeType="positive"
            icon={Bot}
            iconColor="bg-gradient-to-r from-purple-500 to-pink-500"
          />
          <StatCard
            title="Platform Fee"
            value="KES 42,000"
            change="10%"
            changeType="neutral"
            icon={DollarSign}
            iconColor="bg-gradient-to-r from-orange-500 to-yellow-500"
          />
        </div>
        
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
            <AreaChart data={performanceData}>
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
              {recentTransactions.map((transaction) => {
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
              })}
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;

