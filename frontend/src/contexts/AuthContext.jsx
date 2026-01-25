import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/auth';
import { useToast } from './ToastContext';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const { error: showError, success } = useToast();

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const normalizeUser = (userData) => {
    const isAdmin = Boolean(userData?.is_admin || userData?.isAdmin);
    return {
      ...userData,
      is_admin: isAdmin,
      isAdmin: isAdmin,
    };
  };

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      try {
        // Verify token is still valid by fetching user data
        const userData = await authAPI.getCurrentUser();
        const normalized = normalizeUser(userData);
        setUser(normalized);
        setIsAuthenticated(true);
      } catch (error) {
        // Token invalid or expired
        console.error('Auth check failed:', error);
        logout();
      }
    } else {
      setUser(null);
      setIsAuthenticated(false);
    }
    setLoading(false);
  };

  const login = async (emailOrUserId, password) => {
    try {
      const response = await authAPI.login(emailOrUserId, password);
      
      // Store tokens
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);
      
      // Store user data
      const userData = normalizeUser(
        response.user || {
          id: response.user_id,
          username: emailOrUserId.split('@')[0],
          email: emailOrUserId,
          is_admin: response.is_admin || false,
        }
      );

      localStorage.setItem('user', JSON.stringify(userData));
      
      setUser(userData);
      setIsAuthenticated(true);
      
      success('Login successful!');
      return { success: true, user: userData };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Login failed. Please check your credentials.';
      showError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      success('Registration successful!');
      return { success: true, data: response };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Registration failed. Please try again.';
      
      // Handle field-specific errors
      if (error.response?.data) {
        const fieldErrors = Object.entries(error.response.data)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages[0] : messages}`)
          .join(', ');
        showError(fieldErrors || errorMessage);
      } else {
        showError(errorMessage);
      }
      
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

