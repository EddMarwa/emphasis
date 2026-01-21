import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft } from 'lucide-react';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import { useToast } from '../../contexts/ToastContext';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [error, setError] = useState('');
  
  const { success, error: showError } = useToast();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!email) {
      setError('Email is required');
      return;
    }
    
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email');
      return;
    }
    
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      setSent(true);
      setCountdown(60);
      success('Reset code sent to your email!');
      
      // Start countdown
      const interval = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }, 1500);
  };
  
  const handleResend = () => {
    if (countdown > 0) return;
    setSent(false);
    setEmail('');
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-gradient-page">
      <div className="w-full max-w-md animate-fade-in">
        <div className="bg-white rounded-2xl shadow-quantum-lg p-8">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-button-primary rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-2xl font-bold text-white">Q</span>
            </div>
          </div>
          
          {!sent ? (
            <>
              <h2 className="text-3xl font-bold text-text-dark mb-2 text-center">Forgot Password?</h2>
              <p className="text-text-gray mb-8 text-center">
                Enter your email address and we'll send you a code to reset your password.
              </p>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                <Input
                  type="email"
                  label="Email Address"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={error}
                  required
                />
                
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  loading={loading}
                  className="w-full"
                >
                  Send Reset Code
                </Button>
              </form>
              
              <div className="mt-6 text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 text-sm font-medium text-electric-blue hover:text-electric-cyan transition-colors"
                >
                  <ArrowLeft size={16} />
                  Back to Login
                </Link>
              </div>
            </>
          ) : (
            <div className="text-center animate-slide-up">
              <div className="w-20 h-20 bg-gradient-success rounded-full flex items-center justify-center mx-auto mb-6">
                <Mail size={32} className="text-white" />
              </div>
              
              <h2 className="text-2xl font-bold text-text-dark mb-3">Check Your Email</h2>
              <p className="text-text-gray mb-2">
                We've sent a reset code to <span className="font-semibold text-text-dark">{email}</span>
              </p>
              <p className="text-sm text-text-gray mb-6">
                Please check your inbox and enter the code to reset your password.
              </p>
              
              {countdown > 0 && (
                <p className="text-sm text-text-gray mb-4">
                  Resend code in {countdown} seconds
                </p>
              )}
              
              <div className="flex flex-col gap-3">
                {countdown === 0 && (
                  <Button
                    variant="outline"
                    onClick={handleResend}
                    className="w-full"
                  >
                    Resend Code
                  </Button>
                )}
                
                <Link to="/login">
                  <Button
                    variant="primary"
                    className="w-full"
                  >
                    Back to Login
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;

