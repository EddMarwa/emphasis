import React, { createContext, useContext, useState, useCallback } from 'react';
import { ToastContainer } from '../components/common/Toast';

const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  
  const showToast = useCallback((type, message, duration = 5000) => {
    const id = Date.now() + Math.random();
    const newToast = { id, type, message, duration };
    
    setToasts((prev) => [...prev, newToast]);
    
    return id;
  }, []);
  
  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);
  
  const success = useCallback((message, duration) => {
    return showToast('success', message, duration);
  }, [showToast]);
  
  const error = useCallback((message, duration) => {
    return showToast('error', message, duration);
  }, [showToast]);
  
  const warning = useCallback((message, duration) => {
    return showToast('warning', message, duration);
  }, [showToast]);
  
  const info = useCallback((message, duration) => {
    return showToast('info', message, duration);
  }, [showToast]);
  
  return (
    <ToastContext.Provider value={{ success, error, warning, info, showToast }}>
      {children}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </ToastContext.Provider>
  );
};

