import React, { useState, useEffect } from 'react';
import { Copy, Check, Share2, Users, TrendingUp, Award, Trophy } from 'lucide-react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import StatCard from '../components/dashboard/StatCard';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useToast } from '../contexts/ToastContext';
import { referralsAPI } from '../services/referrals';

const Referrals = ({ user, onLogout }) => {
  const [copied, setCopied] = useState(false);
  const [stats, setStats] = useState(null);
  const [referrals, setReferrals] = useState([]);
  const [analytics, setAnalytics] = useState([]);
  const [loading, setLoading] = useState(true);
  const { success, error: showError } = useToast();

  useEffect(() => {
    fetchReferralData();
  }, []);

  const fetchReferralData = async () => {
    try {
      setLoading(true);
      // Fetch stats
      const statsData = await referralsAPI.getStats();
      setStats(statsData);

      // Fetch referrals list
      const referralsData = await referralsAPI.getMyReferrals();
      setReferrals(referralsData);

      // Fetch analytics
      const analyticsData = await referralsAPI.getAnalytics();
      setAnalytics(analyticsData);
    } catch (err) {
      showError(err.response?.data?.error || 'Failed to load referral data');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    success(`${type} copied to clipboard!`);
    setTimeout(() => setCopied(false), 2000);
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
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-xl animate-pulse"></div>
            ))}
          </div>
        ) : stats ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Referrals"
              value={stats.total_referrals}
              change={`${stats.active_referrals} active`}
              changeType="positive"
              icon={Users}
              iconColor="bg-gradient-button-primary"
            />
            <StatCard
              title="Active Referrals"
              value={stats.active_referrals}
              change={stats.total_referrals > 0 ? Math.round((stats.active_referrals / stats.total_referrals) * 100) + '% active rate' : '0% active rate'}
              changeType="positive"
              icon={TrendingUp}
              iconColor="bg-gradient-success"
            />
            <StatCard
              title="Total Earnings"
              value={`KES ${parseFloat(stats.total_bonuses_earned || 0).toLocaleString()}`}
              change={`KES ${parseFloat(stats.total_bonuses_pending || 0).toLocaleString()} pending`}
              changeType="positive"
              icon={Award}
              iconColor="bg-gradient-to-r from-purple-500 to-pink-500"
            />
            <StatCard
              title="Tier 1 Referrals"
              value={stats.tier1_count}
              change={`${stats.tier2_count} Tier 2, ${stats.tier3_count} Tier 3`}
              changeType="info"
              icon={Trophy}
              iconColor="bg-gradient-to-r from-orange-500 to-yellow-500"
            />
          </div>
        ) : null}

        {/* Referral Code & Link */}
        <Card className="p-8">
          <h2 className="text-2xl font-bold text-text-dark mb-6">Your Referral Code & Link</h2>

          <div className="space-y-6">
            {/* Referral Code */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Referral Code</label>
              <div className="flex gap-3">
                <div className="flex-1 p-4 bg-gradient-card-hover rounded-xl border-2 border-electric-cyan font-mono text-lg font-bold text-text-dark">
                  {stats?.referral_code || '—'}
                </div>
                <Button
                  variant={copied ? 'success' : 'primary'}
                  onClick={() => handleCopy(stats?.referral_code || '', 'Referral code')}
                  className="px-6"
                >
                  {copied ? <Check size={20} /> : <Copy size={20} />}
                </Button>
              </div>
            </div>

            {/* Referral Link */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Referral Link</label>
              <div className="flex gap-3 items-end">
                <div className="flex-1 p-4 bg-gray-50 rounded-xl border-2 border-border-gray font-mono text-sm text-text-dark break-all">
                  {stats?.referral_link || '—'}
                </div>
                <Button
                  variant="primary"
                  onClick={() => handleCopy(stats?.referral_link || '', 'Referral link')}
                  className="px-6 flex-shrink-0"
                >
                  {copied ? <Check size={20} /> : <Copy size={20} />}
                </Button>
              </div>
            </div>

            {/* Share Buttons */}
            <div className="flex flex-wrap gap-3 pt-4 border-t border-border-gray">
              <Button
                variant="success"
                onClick={() => {
                  const message = `Join Quantum Capital using my referral code: ${stats?.referral_code}\n\n${stats?.referral_link}`;
                  window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
                }}
                className="flex items-center gap-2"
              >
                <Share2 size={18} />
                Share on WhatsApp
              </Button>
              <Button
                variant="secondary"
                onClick={() => handleCopy(stats?.referral_link || '', 'Link')}
                className="flex items-center gap-2"
              >
                <Share2 size={18} />
                Copy Share Link
              </Button>
            </div>
          </div>
        </Card>

        {/* Referral Analytics */}
        {!loading && analytics && analytics.length > 0 && (
          <Card className="p-6">
            <h2 className="text-xl font-bold text-text-dark mb-6">Referral Analytics (Last 30 Days)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics}>
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
                  dataKey="new_referrals"
                  stroke="#00D9FF"
                  strokeWidth={3}
                  dot={{ fill: '#00D9FF', r: 5 }}
                  activeDot={{ r: 7 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        )}

        {/* My Referrals & Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* My Referrals */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <h2 className="text-xl font-bold text-text-dark mb-6">Your Referrals ({referrals.length})</h2>
              {loading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-200 rounded-xl animate-pulse"></div>
                  ))}
                </div>
              ) : referrals.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-text-gray mx-auto mb-3 opacity-50" />
                  <p className="text-text-gray">No referrals yet. Share your code to get started!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {referrals.map((ref, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                    >
                      <div>
                        <p className="font-semibold text-text-dark">{ref.referee_name || `Referee #${ref.referee_id}`}</p>
                        <p className="text-sm text-text-gray">Joined: {new Date(ref.created_at).toLocaleDateString()}</p>
                      </div>
                      <div className="text-right">
                        <Badge
                          variant={ref.status === 'active' ? 'success' : 'warning'}
                          size="sm"
                          className="mb-2"
                        >
                          {ref.status.charAt(0).toUpperCase() + ref.status.slice(1)}
                        </Badge>
                        <p className="text-sm font-semibold text-emerald-600">
                          Tier {ref.tier_level}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* Quick Actions */}
          <Card className="p-6">
            <h2 className="text-xl font-bold text-text-dark mb-6 flex items-center gap-2">
              <Trophy size={24} className="text-yellow-500" />
              Quick Actions
            </h2>
            <div className="space-y-3">
              <Button
                variant="primary"
                className="w-full"
                onClick={() => window.location.href = '/leaderboard'}
              >
                View Leaderboard
              </Button>
              <Button
                variant="secondary"
                className="w-full"
                onClick={fetchReferralData}
              >
                Refresh Stats
              </Button>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  const message = `Join Quantum Capital! 🚀\n\nUse my referral code: ${stats?.referral_code}\n\n${stats?.referral_link}`;
                  window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
                }}
              >
                Share on WhatsApp
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Referrals;

