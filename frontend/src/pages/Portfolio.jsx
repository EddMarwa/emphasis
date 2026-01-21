import React, { useState, useEffect } from 'react';
import { TrendingUp, Target, Zap, PlusCircle } from 'lucide-react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import { investmentAPI, paymentAPI } from '../services/investment';
import { useToast } from '../contexts/ToastContext';

const Portfolio = ({ user, onLogout }) => {
  const [investments, setInvestments] = useState([]);
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showInvestmentModal, setShowInvestmentModal] = useState(false);
  const [investmentAmount, setInvestmentAmount] = useState('');
  const { success, error: showError } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [investmentsData, balanceData] = await Promise.all([
        investmentAPI.getInvestments(),
        paymentAPI.getBalance(),
      ]);
      setInvestments(investmentsData);
      setBalance(balanceData);
    } catch (err) {
      showError('Failed to load portfolio data');
    }
    setLoading(false);
  };

  const handleCreateInvestment = async () => {
    if (!investmentAmount || parseFloat(investmentAmount) <= 0) {
      showError('Please enter a valid amount');
      return;
    }

    try {
      await investmentAPI.createInvestment({
        amount: parseFloat(investmentAmount),
      });
      success('Investment created successfully');
      setInvestmentAmount('');
      setShowInvestmentModal(false);
      fetchData();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to create investment');
    }
  };

  if (loading) return <Layout user={user} onLogout={onLogout}><div className="p-8">Loading...</div></Layout>;

  const totalInvested = investments.reduce((sum, inv) => sum + parseFloat(inv.amount || 0), 0);
  const activeInvestments = investments.filter(inv => inv.status === 'active').length;
  const averageReturn = balance?.total_profit && totalInvested ? ((balance.total_profit / totalInvested) * 100).toFixed(2) : '0';

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Investment Portfolio</h1>
          <p className="text-text-gray">Track and manage all your active investments</p>
        </div>

        {/* Portfolio Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="p-6">
            <p className="text-sm text-text-gray mb-2">Total Invested</p>
            <p className="text-3xl font-bold text-electric-blue">KES {totalInvested.toLocaleString()}</p>
            <p className="text-xs text-text-gray mt-2">{investments.length} investments</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-text-gray mb-2">Active Investments</p>
            <p className="text-3xl font-bold text-emerald-600">{activeInvestments}</p>
            <p className="text-xs text-text-gray mt-2">{((activeInvestments / investments.length) * 100 || 0).toFixed(0)}% of portfolio</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-text-gray mb-2">Total Return</p>
            <p className="text-3xl font-bold text-teal-600">KES {(balance?.total_profit || 0).toLocaleString()}</p>
            <p className="text-xs text-text-gray mt-2">{averageReturn}% ROI</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-text-gray mb-2">Available Balance</p>
            <p className="text-3xl font-bold text-purple-600">KES {(balance?.current_balance || 0).toLocaleString()}</p>
            <p className="text-xs text-text-gray mt-2">Ready to invest</p>
          </Card>
        </div>

        {/* Create Investment Button */}
        <div>
          <Button
            variant="primary"
            size="lg"
            onClick={() => setShowInvestmentModal(true)}
            className="flex items-center gap-2"
          >
            <PlusCircle size={20} />
            Create New Investment
          </Button>
        </div>

        {/* Investments List */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-text-dark mb-6">Your Investments</h2>
          
          {investments.length === 0 ? (
            <div className="text-center py-12">
              <Target size={48} className="mx-auto text-text-gray mb-4 opacity-50" />
              <p className="text-text-gray mb-4">No investments yet</p>
              <Button variant="primary" onClick={() => setShowInvestmentModal(true)}>
                Create Your First Investment
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {investments.map((investment) => (
                <Card key={investment.id} className="p-6 border border-gray-200">
                  <div className="space-y-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm text-text-gray mb-1">Investment ID</p>
                        <p className="font-mono text-sm">{investment.id}</p>
                      </div>
                      <Badge
                        variant={investment.status === 'active' ? 'success' : investment.status === 'paused' ? 'warning' : 'default'}
                        size="sm"
                      >
                        {investment.status}
                      </Badge>
                    </div>

                    <div className="border-t border-gray-200 pt-4">
                      <p className="text-sm text-text-gray mb-1">Amount Invested</p>
                      <p className="text-2xl font-bold text-electric-blue">
                        KES {parseFloat(investment.amount).toLocaleString()}
                      </p>
                    </div>

                    <div>
                      <p className="text-sm text-text-gray mb-2">Allocation</p>
                      {investment.allocations && investment.allocations.length > 0 ? (
                        <div className="space-y-2">
                          {investment.allocations.map((alloc) => (
                            <div key={alloc.id} className="flex items-between justify-between text-sm bg-gray-50 p-2 rounded">
                              <span>{alloc.name}</span>
                              <span className="font-semibold">{alloc.percentage}%</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-text-gray">No allocations</p>
                      )}
                    </div>

                    <div>
                      <p className="text-sm text-text-gray mb-1">Created</p>
                      <p className="text-sm">{new Date(investment.entry_date).toLocaleDateString()}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Card>

        {/* Investment Modal */}
        {showInvestmentModal && (
          <Modal
            isOpen={showInvestmentModal}
            onClose={() => setShowInvestmentModal(false)}
            title="Create New Investment"
          >
            <div className="space-y-6">
              <div>
                <p className="text-sm text-text-gray mb-4">
                  Your investment will be automatically allocated:
                  <br />• 75% to Active Trading
                  <br />• 25% to Reserve Fund
                </p>
              </div>
              <Input
                label="Investment Amount (KES)"
                type="number"
                placeholder="Enter amount"
                value={investmentAmount}
                onChange={(e) => setInvestmentAmount(e.target.value)}
              />
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-900">
                  <strong>Note:</strong> A 10% platform fee will be applied. Ensure you have sufficient balance.
                </p>
              </div>
              <div className="flex gap-3">
                <Button variant="secondary" onClick={() => setShowInvestmentModal(false)}>
                  Cancel
                </Button>
                <Button variant="primary" onClick={handleCreateInvestment}>
                  Create Investment
                </Button>
              </div>
            </div>
          </Modal>
        )}
      </div>
    </Layout>
  );
};

export default Portfolio;
