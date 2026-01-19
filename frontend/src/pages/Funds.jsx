import React, { useState } from 'react';
import { Wallet, ArrowDownCircle, ArrowUpCircle, Smartphone, Coins, Bitcoin } from 'lucide-react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Modal from '../components/common/Modal';
import { useToast } from '../contexts/ToastContext';

const paymentMethods = [
  { id: 'mpesa', name: 'M-Pesa', icon: Smartphone, color: 'bg-green-500', description: 'Instant deposits via M-Pesa' },
  { id: 'usdt_trc20', name: 'USDT TRC20', icon: Coins, color: 'bg-teal-500', description: 'Low fees, fast transactions' },
  { id: 'usdt_erc20', name: 'USDT ERC20', icon: Coins, color: 'bg-blue-500', description: 'Standard Ethereum network' },
  { id: 'bitcoin', name: 'Bitcoin', icon: Bitcoin, color: 'bg-orange-500', description: 'Bitcoin blockchain' },
];

const Funds = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('deposit');
  const [amount, setAmount] = useState('');
  const [selectedMethod, setSelectedMethod] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const { success, error: showError } = useToast();
  
  const minAmount = activeTab === 'deposit' ? 1000 : 500;
  const maxAmount = activeTab === 'deposit' ? 1000000 : 500000;
  
  const handleSubmit = () => {
    if (!amount || parseFloat(amount) < minAmount) {
      showError(`Minimum amount is KES ${minAmount.toLocaleString()}`);
      return;
    }
    
    if (parseFloat(amount) > maxAmount) {
      showError(`Maximum amount is KES ${maxAmount.toLocaleString()}`);
      return;
    }
    
    if (!selectedMethod) {
      showError('Please select a payment method');
      return;
    }
    
    setShowConfirmModal(true);
  };
  
  const handleConfirm = () => {
    setLoading(true);
    setShowConfirmModal(false);
    
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      success(`${activeTab === 'deposit' ? 'Deposit' : 'Withdrawal'} request submitted successfully!`);
      setAmount('');
      setSelectedMethod('');
    }, 2000);
  };
  
  const selectedMethodData = paymentMethods.find(m => m.id === selectedMethod);
  
  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Funds Management</h1>
          <p className="text-text-gray">Deposit or withdraw funds from your account</p>
        </div>
        
        {/* Tab Toggle */}
        <div className="flex gap-4 bg-white rounded-xl p-2 shadow-quantum">
          <button
            onClick={() => {
              setActiveTab('deposit');
              setAmount('');
              setSelectedMethod('');
            }}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-6 rounded-lg font-semibold transition-all duration-300 ${
              activeTab === 'deposit'
                ? 'bg-gradient-button-primary text-white shadow-lg'
                : 'text-text-gray hover:bg-gray-100'
            }`}
          >
            <ArrowDownCircle size={20} />
            Deposit
          </button>
          <button
            onClick={() => {
              setActiveTab('withdraw');
              setAmount('');
              setSelectedMethod('');
            }}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-6 rounded-lg font-semibold transition-all duration-300 ${
              activeTab === 'withdraw'
                ? 'bg-gradient-button-primary text-white shadow-lg'
                : 'text-text-gray hover:bg-gray-100'
            }`}
          >
            <ArrowUpCircle size={20} />
            Withdraw
          </button>
        </div>
        
        {/* Main Card */}
        <Card className="p-8">
          <div className="space-y-8">
            {/* Amount Input */}
            <div>
              <Input
                type="number"
                label="Amount (KES)"
                placeholder={`Enter amount (min: ${minAmount.toLocaleString()})`}
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
              <div className="mt-2 flex items-center justify-between text-sm text-text-gray">
                <span>Minimum: KES {minAmount.toLocaleString()}</span>
                <span>Maximum: KES {maxAmount.toLocaleString()}</span>
              </div>
              {amount && parseFloat(amount) > 0 && (
                <div className="mt-4 p-4 bg-gradient-card-hover rounded-xl">
                  <div className="flex items-center justify-between">
                    <span className="text-text-gray">Amount:</span>
                    <span className="text-2xl font-bold text-text-dark">
                      KES {parseFloat(amount || 0).toLocaleString()}
                    </span>
                  </div>
                  {activeTab === 'withdraw' && (
                    <div className="mt-2 flex items-center justify-between text-sm">
                      <span className="text-text-gray">Fee (10%):</span>
                      <span className="text-text-dark font-semibold">
                        KES {(parseFloat(amount || 0) * 0.1).toLocaleString()}
                      </span>
                    </div>
                  )}
                  {activeTab === 'withdraw' && (
                    <div className="mt-2 flex items-center justify-between font-semibold">
                      <span className="text-text-dark">You'll receive:</span>
                      <span className="text-emerald-600 text-lg">
                        KES {(parseFloat(amount || 0) * 0.9).toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {/* Payment Methods */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-4">
                Select Payment Method
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {paymentMethods.map((method) => {
                  const Icon = method.icon;
                  const isSelected = selectedMethod === method.id;
                  
                  return (
                    <button
                      key={method.id}
                      onClick={() => setSelectedMethod(method.id)}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 text-left ${
                        isSelected
                          ? 'border-electric-cyan bg-gradient-card-hover shadow-lg'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <div className={`${method.color} w-12 h-12 rounded-lg flex items-center justify-center`}>
                          <Icon size={24} className="text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-text-dark mb-1">{method.name}</h3>
                          <p className="text-sm text-text-gray">{method.description}</p>
                        </div>
                        {isSelected && (
                          <div className="w-5 h-5 bg-electric-cyan rounded-full flex items-center justify-center">
                            <div className="w-2 h-2 bg-white rounded-full"></div>
                          </div>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
            
            {/* Info Box */}
            <div className="p-4 bg-gradient-to-r from-electric-blue/10 to-electric-cyan/10 rounded-xl border border-electric-cyan/20">
              <div className="flex items-start gap-3">
                <Wallet size={20} className="text-electric-blue flex-shrink-0 mt-0.5" />
                <div className="text-sm text-text-gray">
                  <p className="font-semibold text-text-dark mb-1">Important Information</p>
                  <ul className="space-y-1 list-disc list-inside">
                    {activeTab === 'deposit' ? (
                      <>
                        <li>Deposits are processed instantly for M-Pesa</li>
                        <li>Crypto deposits may take 5-30 minutes depending on network</li>
                        <li>Minimum deposit: KES {minAmount.toLocaleString()}</li>
                      </>
                    ) : (
                      <>
                        <li>Withdrawals are processed within 24 hours</li>
                        <li>A 10% platform fee applies to all withdrawals</li>
                        <li>Minimum withdrawal: KES {minAmount.toLocaleString()}</li>
                      </>
                    )}
                  </ul>
                </div>
              </div>
            </div>
            
            {/* Submit Button */}
            <Button
              variant="primary"
              size="lg"
              onClick={handleSubmit}
              loading={loading}
              className="w-full"
            >
              {activeTab === 'deposit' ? 'Proceed with Deposit' : 'Proceed with Withdrawal'}
            </Button>
          </div>
        </Card>
        
        {/* Confirmation Modal */}
        <Modal
          isOpen={showConfirmModal}
          onClose={() => setShowConfirmModal(false)}
          title={`Confirm ${activeTab === 'deposit' ? 'Deposit' : 'Withdrawal'}`}
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowConfirmModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={handleConfirm}>
                Confirm
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-text-gray">Amount:</span>
                  <span className="font-semibold text-text-dark">KES {parseFloat(amount || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-gray">Method:</span>
                  <span className="font-semibold text-text-dark">{selectedMethodData?.name}</span>
                </div>
                {activeTab === 'withdraw' && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-text-gray">Fee (10%):</span>
                      <span className="font-semibold text-text-dark">
                        KES {(parseFloat(amount || 0) * 0.1).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between pt-2 border-t border-gray-200">
                      <span className="font-semibold text-text-dark">You'll receive:</span>
                      <span className="font-bold text-emerald-600">
                        KES {(parseFloat(amount || 0) * 0.9).toLocaleString()}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
            <p className="text-sm text-text-gray">
              {activeTab === 'deposit'
                ? 'Please confirm the deposit details above. You will be redirected to complete the payment.'
                : 'Please confirm the withdrawal details above. The funds will be sent to your selected payment method within 24 hours.'}
            </p>
          </div>
        </Modal>
      </div>
    </Layout>
  );
};

export default Funds;

