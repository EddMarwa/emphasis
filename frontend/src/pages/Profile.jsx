import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, Calendar, Shield, Lock, Save, Camera } from 'lucide-react';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import { useAuth } from '../contexts/AuthContext';
import { userAPI } from '../services/user';
import { useToast } from '../contexts/ToastContext';

const Profile = ({ user: userProp, onLogout }) => {
  const { user: authUser, checkAuth } = useAuth();
  const { success, error: showError } = useToast();
  const user = userProp || authUser;
  
  const [formData, setFormData] = useState({
    firstName: user?.first_name || user?.firstName || '',
    lastName: user?.last_name || user?.lastName || '',
    email: user?.email || '',
    phone: user?.phone || '',
    dateOfBirth: user?.date_of_birth || user?.dateOfBirth || '',
  });
  
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [errors, setErrors] = useState({});
  const [passwordErrors, setPasswordErrors] = useState({});
  
  useEffect(() => {
    if (user) {
      setFormData({
        firstName: user?.first_name || user?.firstName || '',
        lastName: user?.last_name || user?.lastName || '',
        email: user?.email || '',
        phone: user?.phone || '',
        dateOfBirth: user?.date_of_birth || user?.dateOfBirth || '',
      });
    }
  }, [user]);
  
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setErrors({});
    
    const newErrors = {};
    if (!formData.firstName.trim()) newErrors.firstName = 'First name is required';
    if (!formData.lastName.trim()) newErrors.lastName = 'Last name is required';
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }
    if (!formData.phone) newErrors.phone = 'Phone is required';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    setLoading(true);
    
    try {
      const updateData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        date_of_birth: formData.dateOfBirth || null,
      };
      
      await userAPI.updateProfile(updateData);
      success('Profile updated successfully!');
      checkAuth(); // Refresh user data
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to update profile';
      showError(errorMessage);
      
      // Handle field-specific errors
      if (error.response?.data) {
        const fieldErrors = {};
        Object.keys(error.response.data).forEach(field => {
          const messages = error.response.data[field];
          fieldErrors[field] = Array.isArray(messages) ? messages[0] : messages;
        });
        setErrors(fieldErrors);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPasswordErrors({});
    
    const newErrors = {};
    if (!passwordData.currentPassword) newErrors.currentPassword = 'Current password is required';
    if (!passwordData.newPassword) {
      newErrors.newPassword = 'New password is required';
    } else if (passwordData.newPassword.length < 8) {
      newErrors.newPassword = 'Password must be at least 8 characters';
    }
    if (!passwordData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (passwordData.newPassword !== passwordData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setPasswordErrors(newErrors);
      return;
    }
    
    setPasswordLoading(true);
    
    try {
      await userAPI.changePassword(passwordData.currentPassword, passwordData.newPassword);
      success('Password changed successfully!');
      setShowPasswordModal(false);
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to change password';
      showError(errorMessage);
      
      if (error.response?.data) {
        const fieldErrors = {};
        Object.keys(error.response.data).forEach(field => {
          const messages = error.response.data[field];
          fieldErrors[field] = Array.isArray(messages) ? messages[0] : messages;
        });
        setPasswordErrors(fieldErrors);
      }
    } finally {
      setPasswordLoading(false);
    }
  };
  
  const getAccountStatusBadge = () => {
    const status = user?.account_status || user?.status || 'active';
    const variants = {
      active: 'success',
      pending: 'warning',
      suspended: 'error',
      closed: 'neutral',
    };
    return (
      <Badge variant={variants[status] || 'neutral'} size="md">
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };
  
  const getKYCStatusBadge = () => {
    const status = user?.kyc_status || 'unverified';
    const variants = {
      verified: 'success',
      pending: 'warning',
      rejected: 'error',
      unverified: 'neutral',
    };
    return (
      <Badge variant={variants[status] || 'neutral'} size="md">
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };
  
  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-dark mb-2">Profile Settings</h1>
          <p className="text-text-gray">Manage your account information and preferences</p>
        </div>
        
        {/* Account Status Card */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-text-dark">Account Status</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <Shield size={20} className="text-electric-blue" />
                <span className="text-sm font-medium text-text-gray">Account Status</span>
              </div>
              <div className="mt-2">
                {getAccountStatusBadge()}
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <Shield size={20} className="text-electric-blue" />
                <span className="text-sm font-medium text-text-gray">KYC Status</span>
              </div>
              <div className="mt-2">
                {getKYCStatusBadge()}
              </div>
            </div>
            {user?.user_id && (
              <div className="p-4 bg-gray-50 rounded-xl md:col-span-2">
                <div className="flex items-center gap-3 mb-2">
                  <User size={20} className="text-electric-blue" />
                  <span className="text-sm font-medium text-text-gray">UID</span>
                </div>
                <p className="font-mono font-bold text-text-dark text-lg mt-2">{user.user_id}</p>
              </div>
            )}
          </div>
        </Card>
        
        {/* Profile Information */}
        <Card className="p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-text-dark">Personal Information</h2>
            <div className="relative">
              <div className="w-20 h-20 bg-gradient-button-primary rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {formData.firstName?.[0]?.toUpperCase() || formData.lastName?.[0]?.toUpperCase() || 'U'}
              </div>
              <button className="absolute bottom-0 right-0 w-8 h-8 bg-electric-cyan rounded-full flex items-center justify-center border-4 border-white shadow-lg hover:bg-electric-blue transition-colors">
                <Camera size={14} className="text-white" />
              </button>
            </div>
          </div>
          
          <form onSubmit={handleProfileUpdate} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Input
                type="text"
                label="First Name"
                placeholder="John"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                error={errors.first_name || errors.firstName}
                required
              />
              
              <Input
                type="text"
                label="Last Name"
                placeholder="Doe"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                error={errors.last_name || errors.lastName}
                required
              />
            </div>
            
            <Input
              type="email"
              label="Email Address"
              placeholder="john@example.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              error={errors.email}
              required
            />
            
            <Input
              type="tel"
              label="Phone Number"
              placeholder="+254 700 000 000"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              error={errors.phone}
              required
            />
            
            <Input
              type="date"
              label="Date of Birth"
              value={formData.dateOfBirth}
              onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
              error={errors.date_of_birth || errors.dateOfBirth}
            />
            
            <div className="flex gap-4 pt-4">
              <Button
                type="submit"
                variant="primary"
                loading={loading}
                className="flex items-center gap-2"
              >
                <Save size={18} />
                Save Changes
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => setShowPasswordModal(true)}
                className="flex items-center gap-2"
              >
                <Lock size={18} />
                Change Password
              </Button>
            </div>
          </form>
        </Card>
        
        {/* Account Verification Status */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-text-dark mb-4">Verification Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-3">
                <Mail size={20} className={user?.email_verified ? 'text-emerald-500' : 'text-gray-400'} />
                <div>
                  <p className="font-semibold text-text-dark">Email Verification</p>
                  <p className="text-sm text-text-gray">{user?.email || 'Not set'}</p>
                </div>
              </div>
              {user?.email_verified ? (
                <Badge variant="success">Verified</Badge>
              ) : (
                <Button variant="outline" size="sm">
                  Verify Email
                </Button>
              )}
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-3">
                <Phone size={20} className={user?.phone_verified ? 'text-emerald-500' : 'text-gray-400'} />
                <div>
                  <p className="font-semibold text-text-dark">Phone Verification</p>
                  <p className="text-sm text-text-gray">{user?.phone || 'Not set'}</p>
                </div>
              </div>
              {user?.phone_verified ? (
                <Badge variant="success">Verified</Badge>
              ) : (
                <Button variant="outline" size="sm">
                  Verify Phone
                </Button>
              )}
            </div>
          </div>
        </Card>
        
        {/* Change Password Modal */}
        <Modal
          isOpen={showPasswordModal}
          onClose={() => {
            setShowPasswordModal(false);
            setPasswordData({
              currentPassword: '',
              newPassword: '',
              confirmPassword: '',
            });
            setPasswordErrors({});
          }}
          title="Change Password"
          size="md"
          footer={
            <>
              <Button
                variant="secondary"
                onClick={() => {
                  setShowPasswordModal(false);
                  setPasswordData({
                    currentPassword: '',
                    newPassword: '',
                    confirmPassword: '',
                  });
                  setPasswordErrors({});
                }}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handlePasswordChange}
                loading={passwordLoading}
              >
                Change Password
              </Button>
            </>
          }
        >
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <Input
              type="password"
              label="Current Password"
              placeholder="Enter your current password"
              value={passwordData.currentPassword}
              onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
              error={passwordErrors.current_password || passwordErrors.currentPassword}
              required
            />
            
            <Input
              type="password"
              label="New Password"
              placeholder="Enter your new password"
              value={passwordData.newPassword}
              onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
              error={passwordErrors.new_password || passwordErrors.newPassword}
              required
            />
            
            <Input
              type="password"
              label="Confirm New Password"
              placeholder="Confirm your new password"
              value={passwordData.confirmPassword}
              onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
              error={passwordErrors.confirm_password || passwordErrors.confirmPassword}
              required
            />
          </form>
        </Modal>
      </div>
    </Layout>
  );
};

export default Profile;

