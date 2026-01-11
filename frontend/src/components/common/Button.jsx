import React from 'react';

const Button = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  onClick,
  children,
  type = 'button',
  className = '',
  ...props
}) => {
  const baseStyles = 'font-semibold rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-gradient-button-primary text-white shadow-lg hover:shadow-xl hover:-translate-y-0.5 focus:ring-cyan-400',
    secondary: 'bg-white border-2 border-gray-300 text-gray-700 hover:border-electric-cyan hover:text-electric-cyan focus:ring-cyan-400',
    success: 'bg-gradient-button-success text-white shadow-lg hover:shadow-xl hover:-translate-y-0.5 focus:ring-emerald-400',
    danger: 'bg-gradient-button-danger text-white shadow-lg hover:shadow-xl hover:-translate-y-0.5 focus:ring-red-400',
    outline: 'bg-transparent border-2 border-electric-blue text-electric-blue hover:bg-electric-blue hover:text-white focus:ring-cyan-400',
  };
  
  const sizes = {
    sm: 'py-2 px-4 text-sm',
    md: 'py-3 px-6 text-base',
    lg: 'py-4 px-8 text-lg',
  };
  
  const buttonClasses = `${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`;
  
  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="flex items-center justify-center">
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;

