import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, Award, Users } from 'lucide-react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import { referralsAPI } from '../services/referrals';
import { useToast } from '../contexts/ToastContext';

const Leaderboard = ({ user, onLogout }) => {
  const [period, setPeriod] = useState('monthly');
  const [leaderboard, setLeaderboard] = useState([]);
  const [myRanking, setMyRanking] = useState(null);
  const [loading, setLoading] = useState(true);
  const { error: showError } = useToast();

  useEffect(() => {
    fetchLeaderboard();
    fetchMyRanking();
  }, [period]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await referralsAPI.getLeaderboard(period, 100);
      setLeaderboard(data);
    } catch (err) {
      showError(err.response?.data?.error || 'Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchMyRanking = async () => {
    try {
      const data = await referralsAPI.getMyRanking(period);
      setMyRanking(data);
    } catch (err) {
      console.error('Failed to load ranking:', err);
    }
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'bg-gradient-to-r from-yellow-400 to-yellow-600';
    if (rank === 2) return 'bg-gradient-to-r from-gray-300 to-gray-500';
    if (rank === 3) return 'bg-gradient-to-r from-orange-400 to-orange-600';
    return 'bg-gray-100';
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-dark mb-2">Referral Leaderboard</h1>
          <p className="text-text-gray">Top referrers and their achievements</p>
        </div>

        {/* My Ranking Card */}
        {myRanking && myRanking.rank > 0 && (
          <Card className="mb-6 bg-gradient-to-r from-electric-blue to-electric-cyan text-white">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white/80 text-sm mb-1">Your Current Rank</p>
                  <h2 className="text-4xl font-bold">{getRankBadge(myRanking.rank)}</h2>
                </div>
                <div className="text-right">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-white/80 text-xs">Referrals</p>
                      <p className="text-2xl font-bold">{myRanking.total_referrals}</p>
                    </div>
                    <div>
                      <p className="text-white/80 text-xs">Points</p>
                      <p className="text-2xl font-bold">{myRanking.points}</p>
                    </div>
                    <div>
                      <p className="text-white/80 text-xs">Earned</p>
                      <p className="text-2xl font-bold">
                        KES {parseFloat(myRanking.total_bonus_earned).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Period Filter */}
        <div className="mb-6 flex gap-2">
          {['weekly', 'monthly', 'quarterly', 'yearly', 'all_time'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                period === p
                  ? 'bg-electric-blue text-white shadow-lg'
                  : 'bg-white text-text-dark hover:bg-gray-50'
              }`}
            >
              {p.replace('_', ' ').charAt(0).toUpperCase() + p.replace('_', ' ').slice(1)}
            </button>
          ))}
        </div>

        {/* Leaderboard Table */}
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-gray">
                  <th className="px-6 py-4 text-left text-xs font-semibold text-text-gray uppercase">
                    Rank
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-text-gray uppercase">
                    User ID
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-text-gray uppercase">
                    Total Referrals
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-text-gray uppercase">
                    Active
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-text-gray uppercase">
                    Points
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-text-gray uppercase">
                    Total Earned
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-text-gray uppercase">
                    Prize
                  </th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center">
                      <div className="flex justify-center">
                        <div className="w-8 h-8 border-4 border-electric-cyan border-t-transparent rounded-full animate-spin"></div>
                      </div>
                    </td>
                  </tr>
                ) : leaderboard.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center text-text-gray">
                      No leaderboard data available for this period
                    </td>
                  </tr>
                ) : (
                  leaderboard.map((entry) => (
                    <tr
                      key={entry.user_id}
                      className={`border-b border-border-gray hover:bg-gray-50 transition-colors ${
                        entry.user_id === user?.user_id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <td className="px-6 py-4">
                        <div
                          className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-white font-bold ${getRankColor(
                            entry.rank
                          )}`}
                        >
                          {entry.rank <= 3 ? getRankBadge(entry.rank) : entry.rank}
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium text-text-dark">
                        {entry.user_id}
                        {entry.user_id === user?.user_id && (
                          <Badge variant="info" className="ml-2">
                            You
                          </Badge>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right text-text-dark font-semibold">
                        {entry.total_referrals}
                      </td>
                      <td className="px-6 py-4 text-right text-emerald font-semibold">
                        {entry.active_referrals}
                      </td>
                      <td className="px-6 py-4 text-right text-electric-blue font-semibold">
                        {entry.points.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-right text-text-dark font-semibold">
                        KES {parseFloat(entry.total_bonus_earned).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {entry.prize_awarded ? (
                          <div className="flex flex-col items-center">
                            <Trophy className="w-5 h-5 text-yellow-500 mb-1" />
                            <span className="text-xs text-text-gray">{entry.prize_description}</span>
                          </div>
                        ) : (
                          <span className="text-text-gray">—</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Info Card */}
        <Card className="mt-6">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-text-dark mb-4 flex items-center gap-2">
              <Award className="w-5 h-5 text-electric-cyan" />
              How Points are Calculated
            </h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-text-gray">
              <div className="flex items-start gap-2">
                <TrendingUp className="w-4 h-4 text-emerald mt-1" />
                <div>
                  <p className="font-medium text-text-dark">Active Referrals</p>
                  <p>10 points per active referral (Tier 1)</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Users className="w-4 h-4 text-electric-blue mt-1" />
                <div>
                  <p className="font-medium text-text-dark">Multi-tier Bonus</p>
                  <p>5 points (Tier 2), 2 points (Tier 3)</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Trophy className="w-4 h-4 text-yellow-500 mt-1" />
                <div>
                  <p className="font-medium text-text-dark">Earnings Bonus</p>
                  <p>1 point per 1,000 KES earned</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Award className="w-4 h-4 text-electric-cyan mt-1" />
                <div>
                  <p className="font-medium text-text-dark">Prizes</p>
                  <p>Top performers earn special prizes!</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default Leaderboard;
