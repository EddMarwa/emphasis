import React, { useState } from 'react';
import { Copy, Check, Share2, Users, TrendingUp, Award, Trophy } from 'lucide-react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import StatCard from '../components/dashboard/StatCard';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useToast } from '../contexts/ToastContext';

const referralCode = 'KE-QC-00001-REF';
const referralLink = `https://quantumcapital.com/register?ref=${referralCode}`;

const referralStats = [
  { date: 'Jan 1', referrals: 0 },
  { date: 'Jan 8', referrals: 5 },
  { date: 'Jan 15', referrals: 12 },
  { date: 'Jan 22', referrals: 18 },
  { date: 'Jan 29', referrals: 25 },
];

const myReferrals = [
  { id: 1, username: 'user_002', joinedDate: '2024-01-15', status: 'active', earnings: 2500 },
  { id: 2, username: 'user_003', joinedDate: '2024-01-12', status: 'active', earnings: 1800 },
  { id: 3, username: 'user_004', joinedDate: '2024-01-10', status: 'active', earnings: 3200 },
  { id: 4, username: 'user_005', joinedDate: '2024-01-08', status: 'pending', earnings: 0 },
  { id: 5, username: 'user_006', joinedDate: '2024-01-05', status: 'active', earnings: 1500 },
];

const leaderboard = [
  { rank: 1, userId: 'KE-QC-00050', referrals: 125, earnings: 312500 },
  { rank: 2, userId: 'KE-QC-00042', referrals: 98, earnings: 245000 },
  { rank: 3, userId: 'KE-QC-00038', referrals: 87, earnings: 217500 },
  { rank: 4, userId: 'KE-QC-00025', referrals: 76, earnings: 190000 },
  { rank: 5, userId: 'KE-QC-00015', referrals: 65, earnings: 162500 },
  { rank: 6, userId: 'KE-QC-00010', referrals: 54, earnings: 135000 },
  { rank: 7, userId: 'KE-QC-00008', referrals: 43, earnings: 107500 },
  { rank: 8, userId: 'KE-QC-00007', referrals: 38, earnings: 95000 },
  { rank: 9, userId: 'KE-QC-00005', referrals: 32, earnings: 80000 },
  { rank: 10, userId: 'KE-QC-00001', referrals: 25, earnings: 62500 },
];

const Referrals = ({ user, onLogout }) => {
  const [copied, setCopied] = useState(false);
  const { success } = useToast();
  
  const handleCopy = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    success(`${type} copied to clipboard!`);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const handleShareWhatsApp = () => {
    const message = `Join Quantum Capital using my referral code: ${referralCode}\n\n${referralLink}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
  };
  
  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-8 animate-fade-in">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Referral Program</h1>
          <p className="text-text-gray">Earn rewards by inviting others to join Quantum Capital</p>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Referrals"
            value="25"
            change="+5 this month"
            changeType="positive"
            icon={Users}
            iconColor="bg-gradient-button-primary"
          />
          <StatCard
            title="Active Referrals"
            value="20"
            change="80% active rate"
            changeType="positive"
            icon={TrendingUp}
            iconColor="bg-gradient-success"
          />
          <StatCard
            title="Total Earnings"
            value="KES 9,000"
            change="From referrals"
            changeType="positive"
            icon={Award}
            iconColor="bg-gradient-to-r from-purple-500 to-pink-500"
          />
          <StatCard
            title="Your Rank"
            value="#10"
            change="Top 10%"
            changeType="positive"
            icon={Trophy}
            iconColor="bg-gradient-to-r from-orange-500 to-yellow-500"
          />
        </div>
        
        {/* Referral Code & Link */}
        <Card className="p-8">
          <h2 className="text-2xl font-bold text-text-dark mb-6">Your Referral Code & Link</h2>
          
          <div className="space-y-6">
            {/* Referral Code */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Referral Code</label>
              <div className="flex gap-3">
                <div className="flex-1 p-4 bg-gradient-card-hover rounded-xl border-2 border-electric-cyan font-mono text-lg font-bold text-text-dark">
                  {referralCode}
                </div>
                <Button
                  variant={copied ? 'success' : 'primary'}
                  onClick={() => handleCopy(referralCode, 'Referral code')}
                  className="px-6"
                >
                  {copied ? <Check size={20} /> : <Copy size={20} />}
                </Button>
              </div>
            </div>
            
            {/* Referral Link */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Referral Link</label>
              <div className="flex gap-3">
                <Input
                  value={referralLink}
                  readOnly
                  className="font-mono text-sm"
                />
                <Button
                  variant="primary"
                  onClick={() => handleCopy(referralLink, 'Referral link')}
                  className="px-6"
                >
                  {copied ? <Check size={20} /> : <Copy size={20} />}
                </Button>
              </div>
            </div>
            
            {/* Share Buttons */}
            <div className="flex flex-wrap gap-3">
              <Button
                variant="success"
                onClick={handleShareWhatsApp}
                className="flex items-center gap-2"
              >
                <Share2 size={18} />
                Share on WhatsApp
              </Button>
              <Button
                variant="secondary"
                onClick={() => handleCopy(referralLink, 'Link')}
                className="flex items-center gap-2"
              >
                <Share2 size={18} />
                Copy Share Link
              </Button>
            </div>
          </div>
        </Card>
        
        {/* Referral Analytics */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-text-dark mb-6">Referral Analytics</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={referralStats}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                }}
              />
              <Line
                type="monotone"
                dataKey="referrals"
                stroke="#00D9FF"
                strokeWidth={3}
                dot={{ fill: '#00D9FF', r: 5 }}
                activeDot={{ r: 7 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
        
        {/* My Referrals & Leaderboard */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* My Referrals */}
          <Card className="p-6">
            <h2 className="text-xl font-bold text-text-dark mb-6">Your Referrals</h2>
            <div className="space-y-4">
              {myReferrals.map((ref) => (
                <div
                  key={ref.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div>
                    <p className="font-semibold text-text-dark font-mono">{ref.username}</p>
                    <p className="text-sm text-text-gray">Joined: {ref.joinedDate}</p>
                  </div>
                  <div className="text-right">
                    <Badge
                      variant={ref.status === 'active' ? 'success' : 'warning'}
                      size="sm"
                      className="mb-2"
                    >
                      {ref.status}
                    </Badge>
                    <p className="text-sm font-semibold text-emerald-600">
                      KES {ref.earnings.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
          
          {/* Leaderboard */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-text-dark">Leaderboard</h2>
              <Trophy size={24} className="text-yellow-500" />
            </div>
            <div className="space-y-3">
              {leaderboard.map((entry) => (
                <div
                  key={entry.rank}
                  className={`flex items-center justify-between p-4 rounded-xl ${
                    entry.rank <= 3
                      ? 'bg-gradient-card-hover border-2 border-electric-cyan'
                      : 'bg-gray-50 hover:bg-gray-100'
                  } transition-colors`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      entry.rank === 1 ? 'bg-yellow-500 text-white' :
                      entry.rank === 2 ? 'bg-gray-400 text-white' :
                      entry.rank === 3 ? 'bg-orange-500 text-white' :
                      'bg-gray-200 text-text-dark'
                    }`}>
                      {entry.rank}
                    </div>
                    <div>
                      <p className="font-semibold text-text-dark font-mono text-sm">{entry.userId}</p>
                      <p className="text-xs text-text-gray">{entry.referrals} referrals</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-emerald-600">KES {entry.earnings.toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Referrals;

