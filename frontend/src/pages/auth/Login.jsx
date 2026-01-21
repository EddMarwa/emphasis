import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import { useAuth } from '../../contexts/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({
    emailOrUserId: '', // Can be email or user ID
    password: '',
    rememberMe: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.emailOrUserId.trim()) {
      newErrors.emailOrUserId = 'Email or User ID is required';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }
    
    setLoading(true);
    
    try {
      // Pass email or user ID to login function
      const result = await login(formData.emailOrUserId, formData.password);
      
      if (result.success) {
        // Redirect on success
        setTimeout(() => {
          navigate('/dashboard');
        }, 500);
      } else {
        // Error is already shown by auth context
        setErrors({ general: result.error });
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrors({ general: 'An unexpected error occurred. Please try again.' });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex">
      {/* Left Side - Brand Section */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-primary items-center justify-center p-12 text-white">
        <div className="max-w-md animate-fade-in">
          <div className="w-16 h-16 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center mb-8 shadow-cyan-glow">
            <span className="text-3xl font-bold">Q</span>
          </div>
          <h1 className="text-4xl font-bold mb-4">Welcome to Quantum Capital</h1>
          <p className="text-lg opacity-90 leading-relaxed">
            Your gateway to intelligent automated trading. Experience the future of investment with our AI-powered platform.
          </p>
          <div className="mt-8 flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-electric-cyan rounded-full"></div>
              <span>Automated trading powered by AI</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-electric-cyan rounded-full"></div>
              <span>Secure and transparent transactions</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-electric-cyan rounded-full"></div>
              <span>Real-time performance tracking</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gradient-page">
        <div className="w-full max-w-md animate-slide-up">
          <div className="bg-white rounded-2xl shadow-quantum-lg p-8">
            {/* Logo for mobile */}
            <div className="lg:hidden flex justify-center mb-6">
              <div className="w-16 h-16 bg-gradient-button-primary rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-2xl font-bold text-white">Q</span>
              </div>
            </div>
            
            <h2 className="text-3xl font-bold text-text-dark mb-2">Welcome Back</h2>
            <p className="text-text-gray mb-8">Sign in to continue to Quantum Capital</p>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <Input
                type="text"
                label="Email or User ID"
                placeholder="Enter your email or User ID (e.g., KE-QC-00001)"
                value={formData.emailOrUserId}
                onChange={(e) => setFormData({ ...formData, emailOrUserId: e.target.value })}
                error={errors.emailOrUserId || errors.email}
                required
              />
              <p className="text-xs text-text-gray -mt-2 mb-2">
                You can login using your email address or User ID
              </p>
              
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  label="Password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  error={errors.password}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-11 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.rememberMe}
                    onChange={(e) => setFormData({ ...formData, rememberMe: e.target.checked })}
                    className="w-4 h-4 text-electric-blue border-gray-300 rounded focus:ring-electric-cyan"
                  />
                  <span className="text-sm text-text-gray">Remember me</span>
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-electric-blue hover:text-electric-cyan transition-colors"
                >
                  Forgot Password?
                </Link>
              </div>
              
              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={loading}
                className="w-full"
              >
                Sign In
              </Button>
            </form>
            
            <div className="mt-6 text-center">
              <p className="text-text-gray">
                Don't have an account?{' '}
                <Link
                  to="/register"
                  className="font-semibold text-electric-blue hover:text-electric-cyan transition-colors"
                >
                  Create Account
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

