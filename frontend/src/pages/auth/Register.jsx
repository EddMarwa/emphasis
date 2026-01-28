import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Mail, Lock, User, Phone, Eye, EyeOff, ChevronDown, ChevronUp, CheckCircle2, Gift } from 'lucide-react';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import CountrySelect from '../../components/common/CountrySelect';
import Modal from '../../components/common/Modal';
import { useAuth } from '../../contexts/AuthContext';
import { formatPhoneNumber, getCountryByCode } from '../../data/countries';

const Register = () => {
  const [searchParams] = useSearchParams();
  const referralCodeFromUrl = searchParams.get('ref');
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    country: 'KE', // Default to Kenya
    phone: '',
    password: '',
    confirmPassword: '',
    termsAccepted: false,
    referralCode: referralCodeFromUrl || '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [registeredUserId, setRegisteredUserId] = useState('');
  
  const navigate = useNavigate();
  const { register } = useAuth();
  
  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
    return strength;
  };
  
  const handleCountryChange = (countryCode) => {
    setFormData({ ...formData, country: countryCode, phone: '' }); // Reset phone when country changes
  };
  
  const handlePhoneChange = (e) => {
    const value = e.target.value;
    const formatted = formatPhoneNumber(value, formData.country);
    setFormData({ ...formData, phone: formatted });
  };
  
  const handlePasswordChange = (e) => {
    const password = e.target.value;
    setFormData({ ...formData, password });
    setPasswordStrength(calculatePasswordStrength(password));
  };
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }
    
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }
    
    if (!formData.phone) {
      newErrors.phone = 'Phone number is required';
    } else {
      const country = getCountryByCode(formData.country);
      if (!country.phonePattern.test(formData.phone)) {
        newErrors.phone = `Please enter a valid ${country.name} phone number`;
      }
    }
    
    if (!formData.country) {
      newErrors.country = 'Country is required';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (!formData.termsAccepted) {
      newErrors.termsAccepted = 'You must accept the terms and conditions';
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
      const registrationData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        country_code: formData.country,
        password: formData.password,
        confirm_password: formData.confirmPassword,
        referral_code_input: formData.referralCode,
      };
      
      const result = await register(registrationData);
      
      if (result.success) {
        // Show user ID in success modal
        if (result.data?.user_id) {
          setRegisteredUserId(result.data.user_id);
          setShowSuccessModal(true);
        } else {
          // If no user ID in response, redirect to login
          setTimeout(() => {
            navigate('/login');
          }, 1000);
        }
      } else {
        // Handle field-specific errors
        if (result.error) {
          const fieldErrors = {};
          // Parse error messages if they're in format "field: message"
          if (typeof result.error === 'string' && result.error.includes(':')) {
            const parts = result.error.split(',');
            parts.forEach(part => {
              const [field, ...messageParts] = part.split(':');
              if (field && messageParts.length > 0) {
                fieldErrors[field.trim()] = messageParts.join(':').trim();
              }
            });
          }
          setErrors(fieldErrors);
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ general: 'An unexpected error occurred. Please try again.' });
    } finally {
      setLoading(false);
    }
  };
  
  const handleSuccessModalClose = () => {
    setShowSuccessModal(false);
    navigate('/login');
  };
  
  const getStrengthColor = () => {
    if (passwordStrength <= 2) return 'bg-red-500';
    if (passwordStrength <= 3) return 'bg-yellow-500';
    return 'bg-emerald-500';
  };
  
  const getStrengthText = () => {
    if (passwordStrength <= 2) return 'Weak';
    if (passwordStrength <= 3) return 'Medium';
    return 'Strong';
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-gradient-page">
      <div className="w-full max-w-2xl animate-fade-in">
        <div className="bg-white rounded-2xl shadow-quantum-lg p-8">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-button-primary rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-2xl font-bold text-white">Q</span>
            </div>
          </div>
          
          <h2 className="text-3xl font-bold text-text-dark mb-2 text-center">Create Your Account</h2>
          <p className="text-text-gray mb-8 text-center">Join Quantum Capital and start your investment journey</p>
          
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <Input
                type="text"
                label="First Name"
                placeholder="John"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                error={errors.firstName}
                required
              />
              
              <Input
                type="text"
                label="Last Name"
                placeholder="Doe"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                error={errors.lastName}
                required
              />
            </div>
            
            <Input
              type="email"
              label="Email Address"
              placeholder="john.doe@example.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              error={errors.email}
              required
            />
            
            <CountrySelect
              label="Country"
              value={formData.country}
              onChange={handleCountryChange}
              error={errors.country}
              required
            />
            
            <Input
              type="tel"
              label="Phone Number"
              placeholder={getCountryByCode(formData.country).phoneCode + ' ...'}
              value={formData.phone}
              onChange={handlePhoneChange}
              error={errors.phone}
              required
            />

            {formData.referralCode && (
              <div className="p-4 bg-green-50 border-2 border-emerald rounded-xl flex items-center gap-3">
                <Gift className="w-5 h-5 text-emerald flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-text-dark">Referral Code Applied</p>
                  <p className="text-xs text-text-gray">You'll earn a bonus when you make your first deposit!</p>
                </div>
              </div>
            )}
            
            <div>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  label="Password"
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={handlePasswordChange}
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
              
              {formData.password && (
                <div className="mt-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-text-gray">Password Strength:</span>
                    <span className={`text-xs font-medium ${passwordStrength <= 2 ? 'text-red-600' : passwordStrength <= 3 ? 'text-yellow-600' : 'text-emerald-600'}`}>
                      {getStrengthText()}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${getStrengthColor()}`}
                      style={{ width: `${(passwordStrength / 5) * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="relative">
              <Input
                type={showConfirmPassword ? 'text' : 'password'}
                label="Confirm Password"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                error={errors.confirmPassword}
                required
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-4 top-11 text-gray-400 hover:text-gray-600"
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            
            <div>
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.termsAccepted}
                  onChange={(e) => setFormData({ ...formData, termsAccepted: e.target.checked })}
                  className="mt-1 w-4 h-4 text-electric-blue border-gray-300 rounded focus:ring-electric-cyan"
                />
                <span className="text-sm text-text-gray">
                  I agree to the{' '}
                  <Link to="/terms" className="text-electric-blue hover:text-electric-cyan font-medium">
                    Terms and Conditions
                  </Link>{' '}
                  and{' '}
                  <Link to="/privacy" className="text-electric-blue hover:text-electric-cyan font-medium">
                    Privacy Policy
                  </Link>
                </span>
              </label>
              {errors.termsAccepted && (
                <p className="text-sm text-red-600 mt-1">{errors.termsAccepted}</p>
              )}
            </div>
            
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="w-full"
            >
              Create Account
            </Button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-text-gray">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-semibold text-electric-blue hover:text-electric-cyan transition-colors"
              >
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
      
      {/* Success Modal with User ID */}
      <Modal
        isOpen={showSuccessModal}
        onClose={handleSuccessModalClose}
        title="Registration Successful!"
        size="md"
        footer={
          <Button variant="primary" onClick={handleSuccessModalClose} className="w-full">
            Continue to Login
          </Button>
        }
      >
        <div className="text-center space-y-4">
          <div className="w-20 h-20 bg-gradient-success rounded-full flex items-center justify-center mx-auto">
            <CheckCircle2 size={40} className="text-white" />
          </div>
          
          <div>
            <h3 className="text-xl font-bold text-text-dark mb-2">Welcome to Quantum Capital!</h3>
            <p className="text-text-gray mb-4">
              Your account has been created successfully. Please save your User ID - you'll need it to login.
            </p>
          </div>
          
          {registeredUserId && (
            <div className="p-4 bg-gradient-card-hover rounded-xl border-2 border-electric-cyan">
              <p className="text-sm font-medium text-text-gray mb-2">Your User ID:</p>
              <p className="font-mono font-bold text-2xl text-text-dark">{registeredUserId}</p>
              <p className="text-xs text-text-gray mt-2">
                You can use this User ID or your email to login
              </p>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default Register;

