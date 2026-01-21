import React, { useState, useEffect } from 'react';
import { Plus, Send, CreditCard, ArrowDownLeft, ArrowUpRight, Clock, Download } from 'lucide-react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import { paymentAPI } from '../services/investment';
import { useToast } from '../contexts/ToastContext';

const Funds = ({ user, onLogout }) => {
  const [balance, setBalance] = useState(null);
  const [deposits, setDeposits] = useState([]);
  const [withdrawals, setWithdrawals] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [showWithdrawalModal, setShowWithdrawalModal] = useState(false);
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [depositMethod, setDepositMethod] = useState('mpesa');
  const [withdrawMethod, setWithdrawMethod] = useState('mpesa');
  const { success, error: showError } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [balanceData, depositsData, withdrawalsData, txData] = await Promise.all([
        paymentAPI.getBalance(),
        paymentAPI.getDeposits(),
        paymentAPI.getWithdrawals(),
        paymentAPI.getTransactions({ limit: 20 }),
      ]);
      setBalance(balanceData);
      setDeposits(depositsData);
      setWithdrawals(withdrawalsData);
      setTransactions(txData.results || []);
    } catch (err) {
      showError('Failed to load funds data');
    }
    setLoading(false);
  };

  const handleDeposit = async () => {
    if (!depositAmount || parseFloat(depositAmount) <= 0) {
      showError('Please enter a valid amount');
      return;
    }

    try {
      await paymentAPI.createDeposit({
        amount: parseFloat(depositAmount),
        payment_method: depositMethod,
      });
      success('Deposit request created successfully');
      setDepositAmount('');
      setShowDepositModal(false);
      fetchData();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to create deposit');
    }
  };

  const handleWithdrawal = async () => {
    if (!withdrawAmount || parseFloat(withdrawAmount) <= 0) {
      showError('Please enter a valid amount');
      return;
    }

    try {
      await paymentAPI.createWithdrawal({
        amount: parseFloat(withdrawAmount),
        payment_method: withdrawMethod,
      });
      success('Withdrawal request created successfully');
      setWithdrawAmount('');
      setShowWithdrawalModal(false);
      fetchData();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to create withdrawal');
    }
  };

  const handleExport = async () => {
    try {
      const blob = await paymentAPI.exportTransactions();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'transactions.csv';
      a.click();
      success('Transactions exported successfully');
    } catch (err) {
      showError('Failed to export transactions');
    }
  };

  if (loading) return <Layout user={user} onLogout={onLogout}><div className="p-8">Loading...</div></Layout>;

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Funds Management</h1>
          <p className="text-text-gray">Deposit, withdraw, and track your transactions</p>
        </div>

        {/* Balance Card */}
        {balance && (
          <Card className="p-8 bg-gradient-card">
            <div className="space-y-6">
              <div>
                <p className="text-text-gray mb-2">Current Balance</p>
                <p className="text-4xl font-bold text-electric-blue">KES {balance.current_balance?.toLocaleString() || 0}</p>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-text-gray mb-1">Total Deposited</p>
                  <p className="font-bold text-text-dark">KES {balance.total_deposited?.toLocaleString() || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-text-gray mb-1">Total Withdrawn</p>
                  <p className="font-bold text-text-dark">KES {balance.total_withdrawn?.toLocaleString() || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-text-gray mb-1">Total Profit</p>
                  <p className="font-bold text-emerald-600">KES {balance.total_profit?.toLocaleString() || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-text-gray mb-1">Total Fees</p>
                  <p className="font-bold text-red-600">KES {balance.total_fees?.toLocaleString() || 0}</p>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Button
            variant="primary"
            size="lg"
            onClick={() => setShowDepositModal(true)}
            className="flex items-center justify-center gap-2"
          >
            <ArrowDownLeft size={20} />
            Deposit Funds
          </Button>
          <Button
            variant="secondary"
            size="lg"
            onClick={() => setShowWithdrawalModal(true)}
            className="flex items-center justify-center gap-2"
          >
            <ArrowUpRight size={20} />
            Withdraw Funds
          </Button>
        </div>

        {/* Recent Transactions */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-text-dark">Recent Transactions</h2>
            <Button variant="secondary" size="sm" onClick={handleExport} className="flex items-center gap-2">
              <Download size={16} />
              Export CSV
            </Button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Receipt ID</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Type</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Amount</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Status</th>
                  <th className="text-left py-3 px-4 font-semibold text-text-dark">Date</th>
                </tr>
              </thead>
              <tbody>
                {transactions.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center py-6 text-text-gray">No transactions yet</td>
                  </tr>
                ) : (
                  transactions.map((tx) => (
                    <tr key={tx.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-sm">{tx.receipt_id}</td>
                      <td className="py-3 px-4 capitalize">{tx.transaction_type}</td>
                      <td className="py-3 px-4 font-semibold">KES {tx.amount?.toLocaleString()}</td>
                      <td className="py-3 px-4">
                        <Badge variant={tx.status === 'completed' ? 'success' : tx.status === 'failed' ? 'error' : 'warning'} size="sm">
                          {tx.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-text-gray">{new Date(tx.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Deposit Modal */}
        {showDepositModal && (
          <Modal
            isOpen={showDepositModal}
            onClose={() => setShowDepositModal(false)}
            title="Deposit Funds"
          >
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Payment Method</label>
                <select
                  value={depositMethod}
                  onChange={(e) => setDepositMethod(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-electric-blue"
                >
                  <option value="mpesa">M-Pesa</option>
                  <option value="usdt_trc20">USDT TRC20</option>
                  <option value="usdt_erc20">USDT ERC20</option>
                  <option value="bitcoin">Bitcoin</option>
                </select>
              </div>
              <Input
                label="Amount (KES)"
                type="number"
                placeholder="Enter amount"
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
              />
              <div className="flex gap-3">
                <Button variant="secondary" onClick={() => setShowDepositModal(false)}>
                  Cancel
                </Button>
                <Button variant="primary" onClick={handleDeposit}>
                  Proceed with Deposit
                </Button>
              </div>
            </div>
          </Modal>
        )}

        {/* Withdrawal Modal */}
        {showWithdrawalModal && (
          <Modal
            isOpen={showWithdrawalModal}
            onClose={() => setShowWithdrawalModal(false)}
            title="Withdraw Funds"
          >
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Payment Method</label>
                <select
                  value={withdrawMethod}
                  onChange={(e) => setWithdrawMethod(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-electric-blue"
                >
                  <option value="mpesa">M-Pesa</option>
                  <option value="usdt_trc20">USDT TRC20</option>
                  <option value="usdt_erc20">USDT ERC20</option>
                  <option value="bitcoin">Bitcoin</option>
                </select>
              </div>
              <Input
                label="Amount (KES)"
                type="number"
                placeholder="Enter amount"
                value={withdrawAmount}
                onChange={(e) => setWithdrawAmount(e.target.value)}
              />
              <div className="flex gap-3">
                <Button variant="secondary" onClick={() => setShowWithdrawalModal(false)}>
                  Cancel
                </Button>
                <Button variant="primary" onClick={handleWithdrawal}>
                  Request Withdrawal
                </Button>
              </div>
            </div>
          </Modal>
        )}
      </div>
    </Layout>
  );
};

export default Funds;
