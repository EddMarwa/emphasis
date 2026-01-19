import React, { useEffect, useState } from 'react';
import { CheckCircle2, XCircle, AlertCircle, Info, X } from 'lucide-react';

const Toast = ({
  type = 'info',
  message,
  duration = 5000,
  onClose,
  id,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => {
          if (onClose) onClose(id);
        }, 300);
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [duration, id, onClose]);
  
  const icons = {
    success: <CheckCircle2 className="w-5 h-5" />,
    error: <XCircle className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />,
  };
  
  const styles = {
    success: 'bg-gradient-success text-white',
    error: 'bg-gradient-button-danger text-white',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-gradient-button-primary text-white',
  };
  
  if (!isVisible) return null;
  
  return (
    <div
      className={`flex items-center gap-3 p-4 rounded-xl shadow-lg min-w-[300px] max-w-md animate-slide-in-right ${styles[type]}`}
    >
      <div className="flex-shrink-0">
        {icons[type]}
      </div>
      <p className="flex-1 text-sm font-medium">{message}</p>
      <button
        onClick={() => {
          setIsVisible(false);
          setTimeout(() => {
            if (onClose) onClose(id);
          }, 300);
        }}
        className="flex-shrink-0 p-1 hover:bg-white/20 rounded-lg transition-colors"
      >
        <X size={16} />
      </button>
    </div>
  );
};

// Toast Container Component
export const ToastContainer = ({ toasts, onClose }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          type={toast.type}
          message={toast.message}
          duration={toast.duration}
          onClose={onClose}
        />
      ))}
    </div>
  );
};

export default Toast;

